from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.material_repository_interface import IMaterialRepository
from app.models.material import Material
from app.types.exceptions import InvalidFieldError
from app.types.schemas import MaterialPayload


class MaterialRepository(IMaterialRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_material(self, material: MaterialPayload) -> Material:
        db_material = Material(
            name=material.name,
            description=material.description,
            unit_of_measure=material.unit_of_measure,
            stock_quantity=material.stock_quantity,
        )
        self.db.add(db_material)
        self.db.commit()
        self.db.refresh(db_material)
        return db_material

    def get_material_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Material]:
        user_field = getattr(Material, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on material model'
            )
        query = self.db.query(Material).filter(user_field == value)
        if not include_inactive:
            query = query.filter(Material.is_active.is_(True))
        if exclude_id:
            query = query.filter(Material.id != exclude_id)
        return query.first()

    def get_all_materials_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Material], int]:
        query = self.db.query(Material)

        if not include_inactive:
            query = query.filter(Material.is_active.is_(True))

        materials = query.order_by(order).offset(offset).limit(limit).all()
        total_materials = query.count()

        return materials, total_materials

    def delete_material(self, material: Material) -> None:
        material.is_active = False
        material.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_material(self, material: Material) -> Material:
        self.db.commit()
        self.db.refresh(material)
        return material

    def restore_material(self, material: Material) -> Material:
        material.is_active = True
        material.archived_at = None
        self.db.commit()
        self.db.refresh(material)
        return material

    def total_material(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(Material)
        if not include_inactive:
            query = query.filter(Material.is_active.is_(True))
        return query.count()
