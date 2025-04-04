from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.operation import Operation
from app.types.schemas import OperationPayload


class IOperationRepository(ABC):
    @abstractmethod
    def create_operation(self, operation: OperationPayload) -> Operation:
        pass

    @abstractmethod
    def get_operation_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Operation]:
        pass

    @abstractmethod
    def get_all_operations_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Operation], int]:
        pass

    @abstractmethod
    def delete_operation(self, operation: Operation) -> None:
        pass

    @abstractmethod
    def update_operation(self, operation: Operation) -> Operation:
        pass

    @abstractmethod
    def restore_operation(self, operation: Operation) -> Operation:
        pass

    @abstractmethod
    def total_operation(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        pass