from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.mold import Mold
from app.models.part import Part
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.part_repositorie import PartRepository
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import PartBase, PartPayload, PartUpdatePayload


class PartService:
    def __init__(self, db: Session):
        self.part_repo = PartRepository(db)
        self.mold_repo = MoldRepository(db)

    def part_register(self, payload: PartPayload) -> Part:
        self._get_mold_or_404(payload.mold_id)
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.part_repo.total_parts(True) + 1
            payload.name = str(new_name)
        return self.part_repo.create_part(payload)

    def get_all_parts(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Part], int]:
        order_attr = getattr(Part, order_by, None)

        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {order_by} does not exist or is not sortable.'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Part, order_by)) if desc_order else getattr(Part, order_by)
        )
        return self.part_repo.get_all_parts_paginated(offset, limit, order)

    def delete_part(self, id: str) -> None:
        part = self._get_part_or_404(id)
        self.part_repo.delete_part(part)

    def update_part(self, id: str, payload: PartUpdatePayload) -> Part:
        part = self._get_part_or_404(id)

        if payload.name is not None:
            raise InvalidFieldError('Name cannot be changed')

        updated_part = self._update_part_fields(payload, part)
        return self.part_repo.update_part(updated_part)

    def get_part(self, id: str) -> Part:
        return self._get_part_or_404(id)

    def _get_part_or_404(self, id: str) -> Part:
        part = self.part_repo.get_part_by_field('id', id)
        if not part:
            raise NotFoundError('Part not found')
        return part

    def _get_mold_or_404(self, id: str) -> Mold:
        mold = self.mold_repo.get_mold_by_field('id', id)
        if not mold:
            raise NotFoundError('Mold not found')
        return mold

    @staticmethod
    def _update_part_fields(payload: PartBase, target: Part) -> Part:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key):
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.part_repo.get_part_by_field('name', name, exclude_id=exclude_id):
            raise DataConflictError(f"A part with name '{name}' already exists.")
