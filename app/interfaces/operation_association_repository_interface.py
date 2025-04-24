from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.operation import OperationAssociation
from app.types.schemas import OperationAssociationPayload


class IOperationAssociationRepository(ABC):
    @abstractmethod
    def create_operation_association(
        self, operation_association: OperationAssociationPayload
    ) -> OperationAssociation:
        pass

    @abstractmethod
    def get_operation_association_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[OperationAssociation]:
        pass

    @abstractmethod
    def get_all_operation_associations_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
        item_id: Optional[str] = None,
    ) -> Tuple[List[OperationAssociation], int]:
        pass

    @abstractmethod
    def delete_operation_association(
        self, operation_association: OperationAssociation
    ) -> None:
        pass

    @abstractmethod
    def update_operation_association(
        self, operation_association: OperationAssociation
    ) -> OperationAssociation:
        pass

    @abstractmethod
    def restore_operation_association(
        self, operation_association: OperationAssociation
    ) -> OperationAssociation:
        pass

    @abstractmethod
    def get_by_item_and_operation(
        self, item_id: str, operation_id: str, item_type: str, exclude_id: Optional[str] = None
    ) -> OperationAssociation:
        pass
