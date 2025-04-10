from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.operation_association_repository_interface import (
    IOperationAssociationRepository,
)
from app.models.operation import OperationAssociation
from app.types.exceptions import InvalidFieldError
from app.types.schemas import OperationAssociationPayload


class OperationAssociationRepository(IOperationAssociationRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_operation_association(
        self, operation_association: OperationAssociationPayload
    ) -> OperationAssociation:
        db_operation_association = OperationAssociation(
            status=operation_association.status,
            operation_id=operation_association.operation_id,
            item_id=operation_association.item_id,
            item_type=operation_association.item_type,
        )
        self.db.add(db_operation_association)
        self.db.commit()
        self.db.refresh(db_operation_association)
        return db_operation_association

    def get_operation_association_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[OperationAssociation]:
        operation_association_field = getattr(OperationAssociation, field_name, None)
        if not operation_association_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Operation Association model'
            )
        query = self.db.query(OperationAssociation).filter(
            operation_association_field == value
        )
        if not include_inactive:
            query = query.filter(OperationAssociation.is_active.is_(True))
        if exclude_id:
            query = query.filter(OperationAssociation.id != exclude_id)
        return query.first()

    def get_all_operation_association_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
        item_id: Optional[str] = None,
    ) -> Tuple[List[OperationAssociation], int]:
        query = self.db.query(OperationAssociation)

        if not include_inactive:
            query = query.filter(OperationAssociation.is_active.is_(True))

        if item_id:
            query = query.filter(OperationAssociation.item_id == item_id)

        operation_associations = (
            query.order_by(order).offset(offset).limit(limit).all()
        )
        total_operation_associations = query.count()

        return operation_associations, total_operation_associations

    def delete_operation_association(
        self, operation_association: OperationAssociation
    ) -> None:
        operation_association.is_active = False
        operation_association.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_operation_association(
        self, operation_association: OperationAssociation
    ) -> OperationAssociation:
        self.db.commit()
        self.db.refresh(operation_association)
        return operation_association

    def restore_operation_association(
        self, operation_association: OperationAssociation
    ) -> OperationAssociation:
        operation_association.is_active = True
        operation_association.archived_at = None
        self.db.commit()
        self.db.refresh(operation_association)
        return operation_association

    def total_operation_association(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(OperationAssociation)
        if not include_inactive:
            query = query.filter(OperationAssociation.is_active.is_(True))
        return query.count()
