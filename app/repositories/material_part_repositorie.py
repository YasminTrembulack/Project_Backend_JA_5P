from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.material_part_repository_interface import (
    IMaterialPartRepository,
)
from app.models.material import MaterialPart
from app.types.exceptions import InvalidFieldError
from app.types.schemas import MaterialPartPayload


class MaterialPartRepository(IMaterialPartRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_material_part(
        self, material_part: MaterialPartPayload
    ) -> MaterialPart:
        db_material_part = MaterialPart(
            material_id=material_part.material_id,
            part_id=material_part.part_id,
            status=material_part.status,
            quantity=material_part.quantity,
            expected_delivery_date=material_part.expected_delivery_date,
        )
        self.db.add(db_material_part)
        self.db.commit()
        self.db.refresh(db_material_part)
        return db_material_part

    def get_material_part_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[MaterialPart]:
        material_part_field = getattr(MaterialPart, field_name, None)
        if not material_part_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Material Part model'
            )
        query = self.db.query(MaterialPart).filter(material_part_field == value)
        if not include_inactive:
            query = query.filter(MaterialPart.is_active.is_(True))
        if exclude_id:
            query = query.filter(MaterialPart.id != exclude_id)
        return query.first()

    def get_all_material_parts_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
        item_id: Optional[str] = None,
    ) -> Tuple[List[MaterialPart], int]:
        query = self.db.query(MaterialPart)

        if not include_inactive:
            query = query.filter(MaterialPart.is_active.is_(True))

        if item_id:
            query = query.filter(MaterialPart.item_id == item_id)

        total_material_parts = query.count()
        material_parts = query.order_by(order).offset(offset).limit(limit).all()

        return material_parts, total_material_parts

    def delete_material_part(self, material_part: MaterialPart) -> None:
        material_part.is_active = False
        material_part.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_material_part(self, material_part: MaterialPart) -> MaterialPart:
        self.db.commit()
        self.db.refresh(material_part)
        return material_part

    def restore_material_part(self, material_part: MaterialPart) -> MaterialPart:
        material_part.is_active = True
        material_part.archived_at = None
        self.db.commit()
        self.db.refresh(material_part)
        return material_part

    def get_by_part_and_material(
        self, part_id: str, material_id: str, exclude_id: Optional[str] = None
    ) -> Optional[MaterialPart]:
        query = self.db.query(MaterialPart).filter(
            MaterialPart.part_id == part_id,
            MaterialPart.material_id == material_id,
        )

        if exclude_id:
            query = query.filter(MaterialPart.id != exclude_id)

        return query.first()

    def get_by_id_and_status(
        self, part_id: str, status: str, exclude_id: Optional[str] = None
    ) -> Optional[MaterialPart]:
        query = self.db.query(MaterialPart).filter(
            MaterialPart.part_id == part_id,
            MaterialPart.status == status,
        )

        if exclude_id:
            query = query.filter(MaterialPart.id != exclude_id)
        return query.first()
