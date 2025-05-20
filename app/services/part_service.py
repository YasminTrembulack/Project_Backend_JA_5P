from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.mold import Mold
from app.models.part import Part
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.part_repositorie import PartRepository
from app.services.filter_service import FilterService
from app.services.progress_service import ProgressService
from app.types.base import BaseQueryParams, PartBase
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.payload import (
    PaginationParams,
    PartPayload,
    PartUpdatePayload,
)
from app.types.response import (
    MaterialPartResponse,
    MoldResponse,
    OperationAssociationResponse,
)


class PartService:
    def __init__(self, db: Session):
        self.part_repo = PartRepository(db)
        self.mold_repo = MoldRepository(db)
        self.filter_service = FilterService()
        self.progress_service = ProgressService(self.mold_repo, self.part_repo)

    def part_register(self, payload: PartPayload) -> Part:  # ! OK
        self._get_mold_or_404(payload.mold_id)
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.part_repo.total_parts(True) + 1
            payload.name = str(new_name)
        return self.part_repo.create_part(payload)

    def get_all_parts(self, query: BaseQueryParams) -> Tuple[List[Part], int]:
        order_attr = getattr(Part, query.order_by, None)

        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {query.order_by} does not exist or is not sortable.'
            )

        offset = (query.page - 1) * query.limit
        order = desc(order_attr) if query.desc_order else order_attr

        pagination_params = PaginationParams(
            offset=offset,
            limit=query.limit,
        )

        filters, joins = self.filter_service.build_filter(
            'part', query.field, query.value
        )

        return self.part_repo.get_all_parts_paginated(
            pagination_params, order, filters, joins
        )

    @staticmethod
    def configure_associations_response(part: Part, associations: List[str]) -> dict:
        def _load_mold():
            return MoldResponse.model_validate(part.mold.to_dict())

        def _load_operation_associations():
            return [
                OperationAssociationResponse.model_validate(op.to_dict())
                for op in part.operation_associations
            ]

        def _load_material_associations():
            return [
                MaterialPartResponse.model_validate(mat.to_dict())
                for mat in part.material_associations
            ]

        loaders = {
            'mold': _load_mold,
            'operation_associations': _load_operation_associations,
            'material_associations': _load_material_associations,
        }

        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(part, key, None) is not None
        }

    def delete_part(self, id: str) -> None:
        part = self._get_part_or_404(id)
        self.part_repo.delete_part(part)

    def get_part(self, id: str) -> Part:
        return self._get_part_or_404(id)

    def update_part(self, id: str, payload: PartUpdatePayload) -> Part:
        if payload.status is not None:
            raise InvalidFieldError('Status cannot be changed')
        if payload.progress_percentage is not None:
            raise InvalidFieldError('Progress percentage cannot be changed')

        part = self._get_part_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_name = updated_data.get('name', part.name)
        self._validate_name_uniqueness(new_name, part.id)

        new_mold_id = updated_data.get('mold_id', part.mold_id)
        self._get_mold_or_404(new_mold_id)

        its_a_new_3d = True if 'model_3d' in updated_data else False
        its_a_new_nc = True if 'nc_program' in updated_data else False

        updated_part = self._update_part_fields(payload, part)
        new_part = self.part_repo.update_part(updated_part)

        if its_a_new_3d or its_a_new_nc:
            self.progress_service.update_part_progress(new_part.id)

        return new_part

    def _get_mold_or_404(self, id: str) -> Mold:
        mold = self.mold_repo.get_mold_by_field('id', id)
        if not mold:
            raise NotFoundError('Mold not found')
        return mold

    def _get_part_or_404(self, id: str) -> Part:
        part = self.part_repo.get_part_by_field('id', id)
        if not part:
            raise NotFoundError('Part not found')
        return part

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.part_repo.get_part_by_field('name', name, exclude_id=exclude_id):
            raise DataConflictError(f"A part with name '{name}' already exists.")

    @staticmethod
    def _update_part_fields(payload: PartBase, target: Part) -> Part:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key):
                setattr(target, key, value)
        return target
