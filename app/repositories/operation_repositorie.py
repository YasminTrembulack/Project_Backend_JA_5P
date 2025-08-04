from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression, BinaryExpression
from sqlalchemy.orm import Session, joinedload

from app.interfaces.operation_repository_interface import IOperationRepository
from app.models.operation import Operation
from app.types.exceptions import InvalidFieldError
from app.types.payload import OperationPayload, PaginationParams


class OperationRepository(IOperationRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_operation(self, operation: OperationPayload) -> Operation:
        db_operation = Operation(
            name=operation.name,
            op_type=operation.op_type,
            machine_id=operation.machine_id,
        )
        self.db.add(db_operation)
        self.db.commit()
        self.db.refresh(db_operation)
        return db_operation

    def get_operation_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Operation]:
        operation_field = getattr(Operation, field_name, None)
        if not operation_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Operation model'
            )
        query = self.db.query(Operation)

        options = [
            joinedload(Operation.machine),
        ]
        query = query.options(*options)

        query = query.filter(operation_field == value)
        if not include_inactive:
            query = query.filter(Operation.is_active.is_(True))
        if exclude_id:
            query = query.filter(Operation.id != exclude_id)
        return query.first()

    def get_all_operations_paginated(
        self,
        pagination: PaginationParams,
        order: UnaryExpression,
        filters: Optional[BinaryExpression] = None,
        joins: Optional[List] = [],
    ) -> Tuple[List[Operation], int]:
        query = self.db.query(Operation)

        if not pagination.include_inactive:
            query = query.filter(Operation.is_active.is_(True))
        
        if filters is not None:
            for join in joins:
                query = query.join(join)
            query = query.filter(filters)

        total_operations = query.count()
        operations = (
            query.order_by(order)
            .offset(pagination.offset)
            .limit(pagination.limit)
            .all()
        )

        return operations, total_operations

    def delete_operation(self, operation: Operation) -> None:
        operation.is_active = False
        operation.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_operation(self, operation: Operation) -> Operation:
        self.db.commit()
        self.db.refresh(operation)
        return operation

    def restore_operation(self, operation: Operation) -> Operation:
        operation.is_active = True
        operation.archived_at = None
        self.db.commit()
        self.db.refresh(operation)
        return operation

    def total_operation(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(Operation)
        if not include_inactive:
            query = query.filter(Operation.is_active.is_(True))
        return query.count()
