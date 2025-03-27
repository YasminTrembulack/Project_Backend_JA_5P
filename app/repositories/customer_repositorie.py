from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.customer_repository_interface import ICustomerRepository
from app.models.customer import CountryEnum, Customer
from app.types.exceptions import InvalidFieldError
from app.types.schemas import CustomerPayload


class CustomerRepository(ICustomerRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer: CustomerPayload) -> Customer:
        db_customer = Customer(
            full_name=customer.full_name,
            country_code=CountryEnum.get_country_code(customer.country_name),
            country_name=customer.country_name,
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def get_customer_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: bool = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Customer]:
        user_field = getattr(Customer, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Customer model'
            )
        query = self.db.query(Customer).filter(user_field == value)
        if not include_inactive:
            query = query.filter(Customer.is_active.is_(True))
        if exclude_id:
            query = query.filter(Customer.id != exclude_id)
        return query.first()

    def get_all_customers_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: bool = False,
    ) -> Tuple[List[Customer], int]:
        query = self.db.query(Customer)

        if not include_inactive:
            query = query.filter(Customer.is_active.is_(True))

        customers = query.order_by(order).offset(offset).limit(limit).all()
        total_customers = query.count()

        return customers, total_customers

    def delete_customer(self, customer: Customer) -> None:
        customer.is_active = False
        customer.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_customer(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def restore_customer(self, customer: Customer) -> Customer:
        customer.is_active = True
        customer.archived_at = None
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def exists_by_fullname_and_country(
        self,
        full_name: str,
        country_name: str,
        exclude_id: Optional[str] = None,
        include_inactive: bool = False,
    ) -> Customer:
        query = self.db.query(Customer).filter(
            Customer.full_name == full_name, Customer.country_name == country_name
        )
        if exclude_id:
            query = query.filter(Customer.id != exclude_id)

        if not include_inactive:
            query = query.filter(Customer.is_active.is_(True))
        return query.first()
