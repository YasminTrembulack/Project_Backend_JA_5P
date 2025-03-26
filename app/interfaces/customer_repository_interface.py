from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.customer import Customer
from app.types.schemas import CustomerPayload, CustomerUpdatePayload


class ICustomerRepository(ABC):
    @abstractmethod
    def create_customer(self, customer: CustomerPayload) -> Customer:
        pass

    @abstractmethod
    def get_customer_by_field(
        self, field_name: str, value: str
    ) -> Optional[Customer]:
        pass

    @abstractmethod
    def get_all_customer_paginated(
        self, offset: int, limit: int, order: UnaryExpression
    ) -> Tuple[List[Customer], int]:
        pass

    @abstractmethod
    def delete_customer(self, customer: Customer) -> None:
        pass

    @abstractmethod
    def update_customer(
        self, customer: Customer, payload: CustomerUpdatePayload
    ) -> Customer:
        pass
