from datetime import datetime, timedelta
import re
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.part import Part
from app.models.material import Material, MaterialPart
from app.repositories.material_part_repositorie import MaterialPartRepository
from app.repositories.material_repositorie import MaterialRepository
from app.repositories.part_repositorie import PartRepository
from app.types.enums import MaterialStatusEnum, TimeUnitEnum
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.schemas import (
    MaterialPartBase,
    MaterialPartPayload,
    MaterialPartUpdatePayload,
)


class MaterialPartService:
    def __init__(self, db: Session):
        self.material_part_repo = MaterialPartRepository(db)
        self.part_repo = PartRepository(db)
        self.material_repo = MaterialRepository(db)

    def material_part_register(
        self, payload: MaterialPartPayload
    ) -> MaterialPart: 
        self._get_part_or_404(payload.part_id)
        material = self._get_material_or_404(payload.material_id)

        if material.stock_quantity - payload.quantity < 0:
            payload.status = MaterialStatusEnum.PENDING
            payload.expected_delivery_date = self._calcule_delivery_date(
                material.lead_time
            )
        else:
            material.stock_quantity =- payload.quantity
            self.material_repo.update_material(material)
            payload.status = MaterialStatusEnum.AVAILABLE
        
        self._validate_ids(payload.part_id, payload.material_id)
        return self.material_part_repo.create_material_part(payload)

    def get_all_material_part(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[MaterialPart], int]:
        if not hasattr(MaterialPart, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Material Part model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(MaterialPart, order_by))
            if desc_order
            else getattr(MaterialPart, order_by)
        )
        return (
            self.material_part_repo.get_all_material_parts_paginated(
                offset, limit, order
            )
        )

    def delete_material_part(self, id: str) -> None:
        material_part = self._get_material_part_or_404(id)
        return self.material_part_repo.delete_material_part(
            material_part
        )

    def update_material_part(
        self, id: str, payload: MaterialPartUpdatePayload
    ) -> MaterialPart:
        material_part = self._get_material_part_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_part_id = updated_data.get('part_id', material_part.part_id)
        new_material_id = updated_data.get(
            'material_id', material_part.material_id
        )
        
        self._validate_ids(new_part_id, new_material_id, exclude_id=material_part.id)

        updated_material_part = self._update_material_part_fields(
            payload, material_part
        )
        return self.material_part_repo.update_material_part(
            updated_material_part
        )

    def get_material_part(self, id: str) -> MaterialPart:
        return self._get_material_part_or_404(id)

    def _get_material_part_or_404(self, id: str) -> MaterialPart:
        material_part = (
            self.material_part_repo.get_material_part_by_field(
                'id', id
            )
        )
        if not material_part:
            raise NotFoundError('Material Part not found')
        return material_part
    
    def _get_part_or_404(self, id: str) -> Part:
        part = self.part_repo.get_part_by_field('id', id)
        if not part:
            raise NotFoundError('Part not found')
        return part

    def _get_material_or_404(self, id: str) -> Material:
        material = self.material_repo.get_material_by_field('id', id)
        if not material:
            raise NotFoundError('Material not found')
        return material
    
    @staticmethod
    def _update_material_part_fields(
        payload: MaterialPartBase, target: MaterialPart
    ) -> MaterialPart:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target     

    def _validate_ids(
        self, part_id: str, material_id: str, exclude_id: str = None
    ) -> None:
        if self.material_part_repo.get_by_part_and_material(
            part_id, material_id, exclude_id
        ):
            raise DataConflictError(
                'This material is already associated with this part.'
            )

    def _calculate_delivery_date(self, lead_time: str) -> datetime:
        numero, unidade = re.match(r'(\d+)\s*(\w+)', lead_time).groups()
        numero = int(numero)
        unidade = unidade.capitalize()

        if unidade == TimeUnitEnum.DAY.value:
            delta = timedelta(days=numero)
        elif unidade == TimeUnitEnum.WEEK.value:
            delta = timedelta(weeks=numero)
        elif unidade == TimeUnitEnum.MONTH.value:
            delta = timedelta(days=30 * numero)
        elif unidade == TimeUnitEnum.YEAR.value:
            delta = timedelta(days=365 * numero)
        
        return datetime.now() + delta