from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.customer_repository_interface import ICustomerRepository
from app.models.customer import Customer
from app.types.exceptions import InvalidFieldError
from app.types.schemas import CustomerPayload, CustomerUpdatePayload


class CustomerRepository(ICustomerRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer: CustomerPayload) -> Customer:
        db_customer = Customer(
            full_name=customer.full_name,
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def get_customer_by_field(
        self, field_name: str, value: str
    ) -> Optional[Customer]:
        user_field = getattr(Customer, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Customer model'
            )
        return self.db.query(Customer).filter(user_field == value).first()

    def get_all_customers_paginated(
        self, offset: int, limit: int, order: UnaryExpression
    ) -> Tuple[List[Customer], int]:
        customers = (
            self.db.query(Customer)
            .order_by(order)
            .offset(offset)
            .limit(limit)
            .all()
        )
        total_customers = self.db.query(Customer).count()
        return customers, total_customers

    def delete_customer(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.commit()

    def update_customer(
        self, customer: Customer, payload: CustomerUpdatePayload
    ) -> Customer:
        for key, value in payload.items():
            setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer
