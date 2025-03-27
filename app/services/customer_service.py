from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repositorie import CustomerRepository
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import CustomerBase, CustomerPayload, CustomerUpdatePayload


class CustomerService:
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)

    def customer_register(self, payload: CustomerPayload) -> Customer:
        inactive_duplicate = self._get_or_validate_customer_uniqueness(
            payload.full_name, payload.country_name
        )
        if not inactive_duplicate:
            return self.customer_repo.create_customer(payload)
        update_customer = self._update_customer_fields(payload, inactive_duplicate)
        return self.customer_repo.restore_customer(update_customer)

    def get_all_customers(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Customer], int]:
        if not hasattr(Customer, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Customer model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Customer, order_by))
            if desc_order
            else getattr(Customer, order_by)
        )
        return self.customer_repo.get_all_customers_paginated(offset, limit, order)

    def delete_customer(self, id: str) -> None:
        customer = self._get_customer_or_404(id)
        return self.customer_repo.delete_customer(customer)

    def update_customer(self, id: str, payload: CustomerUpdatePayload) -> Customer:
        customer = self._get_customer_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_full_name = updated_data.get('full_name', customer.full_name)
        new_country_name = updated_data.get('country_name', customer.country_name)

        inactive_duplicate = self._get_or_validate_customer_uniqueness(
            new_full_name, new_country_name, customer.id
        )

        if inactive_duplicate:
            self.customer_repo.delete_customer(customer)
            return self.customer_repo.restore_customer(inactive_duplicate)

        updated_customer = self._update_customer_fields(payload, customer)
        return self.customer_repo.update_customer(updated_customer)

    def get_customer(self, id: str) -> Customer:
        return self._get_customer_or_404(id)

    def _get_or_validate_customer_uniqueness(
        self, full_name: str, country_name: str, customer_id: str = None
    ) -> Customer | None:
        if customer := self.customer_repo.exists_by_fullname_and_country(
            full_name, country_name, exclude_id=customer_id, include_inactive=True
        ):
            if customer.is_active:
                raise DataConflictError(
                    f"A customer with name '{full_name}' in country '{country_name}'\
                    already exists"
                )
            return customer
        return None

    def _get_customer_or_404(self, id: str) -> Customer:
        customer = self.customer_repo.get_customer_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')
        return customer

    @staticmethod
    def _update_customer_fields(payload: CustomerBase, target: Customer) -> Customer:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target
