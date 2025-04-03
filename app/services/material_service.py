from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.material import Material
from app.repositories.material_repositorie import MaterialRepository
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import MaterialBase, MaterialPayload, MaterialUpdatePayload


class MaterialService:
    def __init__(self, db: Session):
        self.material_repo = MaterialRepository(db)

    def material_register(self, payload: MaterialPayload) -> Material:
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.material_repo.total_material(True)
            payload.name = str(new_name)
        return self.material_repo.create_part(payload)

    def get_all_materials(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Material], int]:
        if not hasattr(Material, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Material model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Material, order_by))
            if desc_order
            else getattr(Material, order_by)
        )
        return self.material_repo.get_all_materials_paginated(offset, limit, order)

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
        if self.material_repo.get_material_by_field('name', name, exclude_id):
            raise DataConflictError(f"A material with name '{name}' already exists.")
