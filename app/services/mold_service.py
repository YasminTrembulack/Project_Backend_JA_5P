from datetime import date
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.customer import Customer
from app.models.mold import Mold
from app.repositories.customer_repositorie import CustomerRepository
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.part_repositorie import PartRepository
from app.services.progress_service import ProgressService
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import MoldBase, MoldPayload, MoldUpdatePayload


class MoldService:
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.mold_repo = MoldRepository(db)
        self.part_repo = PartRepository(db)
        self.progress_service = ProgressService(self.mold_repo, self.part_repo)

    def mold_register(self, payload: MoldPayload) -> Mold:
        self._get_customer_or_404(payload.customer_id)
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.mold_repo.total_molds(True) + 1
            payload.name = str(new_name)
        return self.mold_repo.create_mold(payload)

    def get_all_molds(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Mold], int]:
        order_attr = getattr(Mold, order_by, None)

        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {order_by} does not exist or is not sortable.'
            )
        offset = (page - 1) * limit

        order_attr = getattr(Mold, order_by)
        order = desc(order_attr) if desc_order else order_attr

        molds, total_molds = self.mold_repo.get_all_molds_paginated(
            offset, limit, order
        )
        return [self._calculate_priority(m) for m in molds], total_molds

    def _get_customer_or_404(self, id: str) -> Customer:
        customer = self.customer_repo.get_customer_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')
        return customer

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.mold_repo.get_mold_by_field('name', name, exclude_id=exclude_id):
            raise DataConflictError(f"A mold with name '{name}' already exists.")

    def delete_mold(self, id: str) -> None:
        mold = self._get_mold_or_404(id)
        self.mold_repo.delete_mold(mold)

    def update_mold(self, id: str, payload: MoldUpdatePayload) -> Mold:
        if payload.progress_percentage is not None:
            raise InvalidFieldError('Progress percentage cannot be changed')
        if payload.priority is not None:
            raise InvalidFieldError('Priority cannot be changed')

        mold = self._get_mold_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_name = updated_data.get('name', mold.name)
        self._validate_name_uniqueness(new_name, mold.id)

        its_a_new_delivery_date = True if 'delivery_date' in updated_data else False

        updated_mold = self._update_mold_fields(payload, mold)

        if its_a_new_delivery_date:
            return self._calculate_priority(mold)

        return self.mold_repo.update_mold(updated_mold)

    def get_mold(self, id: str) -> Mold:
        mold = self._get_mold_or_404(id)
        return self._calculate_priority(mold)

    def _get_mold_or_404(self, id: str) -> Mold:
        mold = self.mold_repo.get_mold_by_field('id', id)
        if not mold:
            raise NotFoundError('Mold not found')
        return mold

    def _calculate_priority(self, mold: Mold) -> Mold:
        # if mold.priority_updated_at != date.today():
        mold.priority_updated_at = date.today()
        mold.progress_percentage = (
            self.progress_service._calculate_mold_progress_percentage(
                mold.mold_parts
            )
        )
        mold.priority = self.progress_service.calculate_priority(
            mold.delivery_date, mold.progress_percentage
        )
        mold = self.mold_repo.update_mold(mold)
        return mold

    @staticmethod
    def _update_mold_fields(payload: MoldBase, target: Mold) -> Mold:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key):
                setattr(target, key, value)
        return target
