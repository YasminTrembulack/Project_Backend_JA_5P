from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.machine import Machine
from app.models.operation import Operation
from app.repositories.machine_repositorie import MachineRepository
from app.repositories.operation_repositorie import OperationRepository
from app.services.filter_service import FilterService
from app.types.base import BaseQueryParams, OperationBase
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.payload import (
    OperationPayload,
    OperationUpdatePayload,
    PaginationParams,
)
from app.types.response import MachineResponse


class OperationService:
    def __init__(self, db: Session):
        self.filter_service = FilterService()
        self.machine_repo = MachineRepository(db)
        self.operation_repo = OperationRepository(db)

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
        self, query: BaseQueryParams
    ) -> Tuple[List[Operation], int]:
        order_attr = getattr(Operation, query.order_by, None)
        
        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {query.order_by} does not exist on Operation model'
            )
        offset = (query.page - 1) * query.limit
        order = desc(order_attr) if query.desc_order else order_attr
        
        pagination_params = PaginationParams(
            offset=offset,
            limit=query.limit,
        )

        filters, joins = self.filter_service.build_filter(
            'operation', query.field, query.value
        )
        
        return self.operation_repo.get_all_operations_paginated(
            pagination_params, order, filters, joins
        )

    @staticmethod
    def configure_associations_response(
        operation: Operation, associations: List[str]
    ) -> dict:
        def _load_machine():
            return MachineResponse.model_validate(operation.machine.to_dict())

        loaders = {
            'machine': _load_machine,
        }
        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(operation, key, None) is not None
        }

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
    def _update_operation_fields(
        payload: OperationBase, target: Operation
    ) -> Operation:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.operation_repo.get_operation_by_field(
            'name', name, exclude_id=exclude_id
        ):
            raise DataConflictError(
                f"A operation with name '{name}' already exists."
            )
