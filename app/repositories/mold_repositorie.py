from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session, joinedload

from app.interfaces.mold_repository_interface import IMoldRepository
from app.models.mold import Mold
from app.types.exceptions import InvalidFieldError
from app.types.schemas import MoldPayload


class MoldRepository(IMoldRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_mold(self, mold: MoldPayload) -> Mold:
        db_mold = Mold(
            name=mold.name,
            status=mold.status,
            quantity=mold.quantity,
            priority=mold.priority,
            dimensions=mold.dimensions,
            delivery_date=mold.delivery_date,
            customer_id=mold.customer_id,
            created_by_id=mold.created_by_id,
        )
        self.db.add(db_mold)
        self.db.commit()
        self.db.refresh(db_mold)
        return db_mold

    def get_mold_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Mold]:
        mold_field = getattr(Mold, field_name, None)
        if not mold_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Mold model'
            )
        query = self.db.query(Mold).filter(mold_field == value)

        if not include_inactive:
            query = query.filter(Mold.is_active.is_(True))
        if exclude_id:
            query = query.filter(Mold.id != exclude_id)
        return query.first()

    def get_all_molds_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        parts: Optional[bool] = False,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Mold], int]:
        query = self.db.query(Mold)
        options = [
            joinedload(Mold.created_by),
            joinedload(Mold.customer),
        ]
        if parts:
            options.append(joinedload(Mold.mold_parts))

        query = query.options(*options)
        if not include_inactive:
            query = query.filter(Mold.is_active.is_(True))

        molds = query.order_by(order).offset(offset).limit(limit).all()
        total_molds = query.count()

        return molds, total_molds

    def delete_mold(self, mold: Mold) -> None:
        mold.is_active = False
        mold.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_mold(self, mold: Mold) -> Mold:
        self.db.commit()
        self.db.refresh(mold)
        return mold

    def restore_mold(self, mold: Mold) -> Mold:
        mold.is_active = True
        mold.archived_at = None
        self.db.commit()
        self.db.refresh(mold)
        return mold

    def total_molds(self, include_inactive: Optional[bool] = False,) -> int:
        query = self.db.query(Mold)
        if not include_inactive:
            query = query.filter(Mold.is_active.is_(True))
        return query.count()
