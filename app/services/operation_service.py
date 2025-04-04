from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.operation import Operation
from app.repositories.operation_repositorie import OperationRepository
from app.repositories.machine_repositorie import MachineRepository
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import OperationBase, OperationPayload, OperationUpdatePayload


class OperationService:
    def __init__(self, db: Session):
        self.operation_repo = OperationRepository(db)
        self.machine_repo = MachineRepository(db)

    def operation_register(self, payload: OperationPayload) -> Operation:
        if payload.machine_id:
            self._get_machine_or_404()
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.operation_repo.total_operation(True) + 1
            payload.name = str(new_name)
        return self.operation_repo.create_operation(payload)

    def get_all_operations(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Operation], int]:
        if not hasattr(Operation, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Operation model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Operation, order_by))
            if desc_order
            else getattr(Operation, order_by)
        )
        return self.operation_repo.get_all_operations_paginated(offset, limit, order)

    def delete_operation(self, id: str) -> None:
        operation = self._get_operation_or_404(id)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        operation.name = f'deleted_{timestamp}_{operation.name}'
        return self.operation_repo.delete_operation(operation)

    def update_operation(
        self, id: str, payload: OperationUpdatePayload
    ) -> Operation:
        operation = self._get_operation_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_name = updated_data.get('name', operation.name)

        self._validate_name_uniqueness(new_name, id)

        updated_operation = self._update_operation_fields(payload, operation)
        return self.operation_repo.update_operation(updated_operation)

    def get_operation(self, id: str) -> Operation:
        return self._get_operation_or_404(id)

    def _get_operation_or_404(self, id: str) -> Operation:
        operation = self.operation_repo.get_operation_by_field('id', id)
        if not operation:
            raise NotFoundError('Operation not found')
        return operation
    
    def _get_machine_or_404(self, id: str) -> Machine:
        machine = self.machine_repo.get_machine_by_field('id', id)
        if not machine:
            raise NotFoundError('Machine not found')
        return machine

    @staticmethod
    def _update_operation_fields(payload: OperationBase, target: Operation) -> Operation:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.operation_repo.get_operation_by_field('name', name, exclude_id):
            raise DataConflictError(
                f"A operation with name '{name}' already exists."
            )
