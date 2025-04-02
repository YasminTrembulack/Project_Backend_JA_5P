from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.part_repository_interface import IPartRepository
from app.models.part import Part
from app.types.exceptions import InvalidFieldError
from app.types.schemas import PartPayload


class PartRepository(IPartRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_part(self, part: PartPayload) -> Part:
        db_part = Part(
            name=part.name,
            model_3d=part.model_3d,
            nc_program=part.nc_program,
            mold_id=part.mold_id,
            status=part.status,
            quantity=part.quantity,
            description=part.description,
        )
        self.db.add(db_part)
        self.db.commit()
        self.db.refresh(db_part)
        return db_part

    def get_part_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Part]:
        part_field = getattr(Part, field_name, None)
        if not part_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Part model'
            )
        query = self.db.query(Part).filter(part_field == value)
        if not include_inactive:
            query = query.filter(Part.is_active.is_(True))
        if exclude_id:
            query = query.filter(Part.id != exclude_id)
        return query.first()

    def get_all_parts_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Part], int]:
        query = self.db.query(Part)

        if not include_inactive:
            query = query.filter(Part.is_active.is_(True))

        parts = query.order_by(order).offset(offset).limit(limit).all()
        total_parts = query.count()

        return parts, total_parts

    def delete_part(self, part: Part) -> None:
        part.is_active = False
        part.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_part(self, part: Part) -> Part:
        self.db.commit()
        self.db.refresh(part)
        return part

    def restore_part(self, part: Part) -> Part:
        part.is_active = True
        part.archived_at = None
        self.db.commit()
        self.db.refresh(part)
        return part

    def total_parts(self, include_inactive: Optional[bool] = False,) -> int:
        query = self.db.query(Part)
        if not include_inactive:
            query = query.filter(Part.is_active.is_(True))
        return query.count()
