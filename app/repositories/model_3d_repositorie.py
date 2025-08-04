from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import BinaryExpression, UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.model_3d_repository_interface import IModel3DRepository
from app.models.model_3d import Model3D
from app.types.exceptions import InvalidFieldError
from app.types.payload import PaginationParams, Model3DPayload


class Model3DRepository(IModel3DRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_model_3d(self, model_3d: Model3DPayload) -> Model3D:
        db_model_3d = Model3D(
            name=model_3d.name,
            responsible=model_3d.responsible,
            path=model_3d.path
        )
        self.db.add(db_model_3d)
        self.db.commit()
        self.db.refresh(db_model_3d)
        return db_model_3d

    def get_model_3d_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Model3D]:
        model_3d_field = getattr(Model3D, field_name, None)
        if not model_3d_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Model3D model'
            )
        query = self.db.query(Model3D).filter(model_3d_field == value)
        if not include_inactive:
            query = query.filter(Model3D.is_active.is_(True))
        if exclude_id:
            query = query.filter(Model3D.id != exclude_id)
        return query.first()

    def get_all_model_3ds_paginated(
        self,
        pagination: PaginationParams,
        order: UnaryExpression,
        filters: Optional[BinaryExpression] = None,
        joins: Optional[List] = [],
    ) -> Tuple[List[Model3D], int]:
        query = self.db.query(Model3D)

        if not pagination.include_inactive:
            query = query.filter(Model3D.is_active.is_(True))

        if filters is not None:
            for join in joins:
                query = query.join(join)
            query = query.filter(filters)

        total_model_3ds = query.count()
        model_3ds = (
            query.order_by(order)
            .offset(pagination.offset)
            .limit(pagination.limit)
            .all()
        )

        return model_3ds, total_model_3ds

    def delete_model_3d(self, model_3d: Model3D) -> None:
        model_3d.is_active = False
        model_3d.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_model_3d(self, model_3d: Model3D) -> Model3D:
        self.db.commit()
        self.db.refresh(model_3d)
        return model_3d

    def restore_model_3d(self, model_3d: Model3D) -> Model3D:
        model_3d.is_active = True
        model_3d.archived_at = None
        self.db.commit()
        self.db.refresh(model_3d)
        return model_3d

    def total_model_3ds(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(Model3D)
        if not include_inactive:
            query = query.filter(Model3D.is_active.is_(True))
        return query.count()
