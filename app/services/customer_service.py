from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.customer import Customer
from app.repositories.customer_repositorie import CustomerRepository
from app.services.filter_service import FilterService
from app.types.base import BaseQueryParams, CustomerBase
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.payload import (
    CustomerPayload,
    CustomerUpdatePayload,
    PaginationParams,
)
from app.types.response import MoldResponse


class CustomerService:
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.filter_service = FilterService()

    def customer_register(self, payload: CustomerPayload) -> Customer:
        inactive_duplicate = self._get_or_validate_customer_uniqueness(
            payload.full_name, payload.country_name
        )
        if not inactive_duplicate:
            return self.customer_repo.create_customer(payload)
        update_customer = self._update_customer_fields(payload, inactive_duplicate)
        return self.customer_repo.restore_customer(update_customer)

    def get_all_customers(
        self, query: BaseQueryParams
    ) -> Tuple[List[Customer], int]:
        order_attr = getattr(Customer, query.order_by, None)

        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {query.order_by} does not exist or is not sortable.'
            )

        offset = (query.page - 1) * query.limit
        order = desc(order_attr) if query.desc_order else order_attr

        pagination_params = PaginationParams(
            offset=offset,
            limit=query.limit,
        )
        filters, joins = self.filter_service.build_filter(
            'customer', query.field, query.value
        )

        return self.customer_repo.get_all_customers_paginated(
            pagination_params, order, filters, joins
        )

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

    @staticmethod
    def configure_associations_response(
        customer: Customer, associations: List[str]
    ) -> dict:
        def _load_molds():
            return [MoldResponse.model_validate(c.to_dict()) for c in customer.molds]

        loaders = {
            'molds': _load_molds,
        }

        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(customer, key, None) is not None
        }

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
