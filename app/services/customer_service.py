from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repositorie import CustomerRepository
from app.types.exceptions import DataConflictError, NotFoundError
from app.types.schemas import CustomerPayload, CustomerUpdatePayload


class CustomerService:
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)

    def customer_register(self, customer: CustomerPayload) -> Customer:
        self._validate_unique_fields(customer.to_dict())
        return self.customer_repo.create_customer(customer)

    def get_all_customers(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Customer], int]:
        offset = (page - 1) * limit
        order = (
            desc(getattr(Customer, order_by))
            if desc_order
            else getattr(Customer, order_by)
        )
        return self.customer_repo.get_all_customers_paginated(offset, limit, order)

    def delete_customer(self, id: str) -> None:
        customer = self.customer_repo.get_customer_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')
        return self.customer_repo.delete_customer(customer)

    def update_customer(self, id: str, payload: CustomerUpdatePayload) -> Customer:
        customer = self.customer_repo.get_user_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')

        self._validate_unique_fields(payload.to_dict(), customer.id)
        payload = payload.model_dump(exclude_unset=True)
        return self.customer_repo.update_customer(customer, payload)

    def get_customer(self, id: str) -> Customer:
        customer = self.customer_repo.get_customer_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')
        return customer

    def _validate_unique_fields(self, payload: dict, customer_id: str = None):
        if payload.get('full_name', False) and self._is_field_in_use(
            'full_name', payload.get('full_name'), customer_id
        ):
            raise DataConflictError('Full name already in use.')

    def _is_field_in_use(self, field: str, value: str, customer_id: str) -> bool:
        existing_customer = self.customer_repo.get_customer_by_field(field, value)
        if not customer_id:
            return existing_customer is not None
        return existing_customer is not None and existing_customer.id != customer_id
