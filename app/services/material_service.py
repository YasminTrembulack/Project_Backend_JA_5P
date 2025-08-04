import re
from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.material import Material
from app.repositories.material_repositorie import MaterialRepository
from app.services.filter_service import FilterService
from app.types.base import BaseQueryParams, MaterialBase
from app.types.enums import TimeUnitEnum
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    InvalidLeadTimeError,
    NotFoundError,
)
from app.types.payload import (
    MaterialPayload,
    MaterialUpdatePayload,
    PaginationParams,
)
from app.types.response import MaterialPartResponse, PartResponse


class MaterialService:
    def __init__(self, db: Session):
        self.material_repo = MaterialRepository(db)
        self.filter_service = FilterService()

    def material_register(self, payload: MaterialPayload) -> Material:
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.material_repo.total_material(True) + 1
            payload.name = str(new_name)
        if not self._validate_lead_time(payload.lead_time):
            raise InvalidLeadTimeError(
                f"Invalid lead time format. Received: '{payload.lead_time}'"
            )

        return self.material_repo.create_material(payload)

    def get_all_materials(self,  query: BaseQueryParams) -> Tuple[List[Material], int]:
        order_attr = getattr(Material, query.order_by, None)
        
        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {query.order_by} does not exist on Material model'
            )
        offset = (query.page - 1) * query.limit
        order = desc(order_attr) if query.desc_order else order_attr
        
        pagination_params = PaginationParams(
            offset=offset,
            limit=query.limit,
        )

        filters, joins = self.filter_service.build_filter(
            'material', query.field, query.value
        )
        
        return self.material_repo.get_all_materials_paginated(
            pagination_params, order, filters, joins
        )

    def delete_material(self, id: str) -> None:
        material = self._get_material_or_404(id)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        material.name = f'deleted_{timestamp}_{material.name}'
        return self.material_repo.delete_material(material)

    def update_material(self, id: str, payload: MaterialUpdatePayload) -> Material:
        material = self._get_material_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_name = updated_data.get('name', material.name)

        self._validate_name_uniqueness(new_name, id)

        updated_material = self._update_material_fields(payload, material)
        return self.material_repo.update_material(updated_material)

    def get_material(self, id: str) -> Material:
        return self._get_material_or_404(id)

    def _get_material_or_404(self, id: str) -> Material:
        material = self.material_repo.get_material_by_field('id', id)
        if not material:
            raise NotFoundError('Material not found')
        return material

    @staticmethod
    def _update_material_fields(payload: MaterialBase, target: Material) -> Material:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.material_repo.get_material_by_field(
            'name', name, exclude_id=exclude_id
        ):
            raise DataConflictError(f"A material with name '{name}' already exists.")

    @staticmethod
    def configure_associations_response(
        material: Material, associations: List[str]
    ) -> dict:
        def _load_parts():
            return [PartResponse.model_validate(p.to_dict()) for p in material.parts]

        def _load_part_associations():
            return [
                MaterialPartResponse.model_validate(mp.to_dict())
                for mp in material.part_associations
            ]

        loaders = {
            'parts': _load_parts,
            'part_associations': _load_part_associations,
        }

        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(material, key, None) is not None
        }

    @staticmethod
    def _validate_lead_time(lead_time: str) -> bool:
        match = re.match(r'^\s*(\d+)\s*(\w+)\s*$', lead_time)
        if not match:
            return False

        numero_str, unidade_str = match.groups()

        try:
            int(numero_str)
        except ValueError:
            return False

        try:
            TimeUnitEnum(unidade_str.capitalize())
        except ValueError:
            return False

        return True
