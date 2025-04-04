from datetime import datetime
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.customer import Customer
from app.models.mold import Mold
from app.models.part import Part
from app.repositories.customer_repositorie import CustomerRepository
from app.repositories.mold_repositorie import MoldRepository
from app.types.enums import PartStatusEnum, PriorityEnum
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import MoldBase, MoldUpdatePayload, PartPayload

URGENT_DAYS_THRESHOLD = 5
HIGH_DAYS_THRESHOLD = 10
MEDIUM_DAYS_THRESHOLD = 20

URGENT_PRIORITY_THRESHOLD = 6
HIGH_PRIORITY_THRESHOLD = 4
MEDIUM_PRIORITY_THRESHOLD = 2


class MoldService:
    def __init__(self, db: Session):
        self.mold_repo = MoldRepository(db)
        self.customer_repo = CustomerRepository(db)

    def part_register(self, payload: PartPayload) -> Mold:
        self._get_customer_or_404(payload.mold_id)
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.mold_repo.total_molds(True) + 1
            payload.name = str(new_name)
        return self.mold_repo.create_mold(payload)

    def _get_all_molds(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Part], int]:
        order_attr = getattr(Part, order_by, None)

        if not isinstance(order_attr, InstrumentedAttribute):
            raise InvalidFieldError(
                f'Field {order_by} does not exist or is not sortable.'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Part, order_by)) if desc_order else getattr(Part, order_by)
        )
        return self.part_repo.get_all_parts_paginated(offset, limit, order)

    def delete_mold(self, id: str) -> None:
        mold = self._get_mold_or_404(id)
        self.mold_repo.delete_mold(mold)

    def update_mold(self, id: str, payload: MoldUpdatePayload) -> Mold:
        mold = self._get_mold_or_404(id)

        if payload.priority is not None:
            raise InvalidFieldError('Priority cannot be changed')

        updated_mold = self._update_mold_fields(payload, mold)
        return self.mold_repo.update_mold(updated_mold)

    def get_mold(self, id: str) -> Mold:
        return self._get_mold_or_404(id)

    def _get_customer_or_404(self, id: str) -> Customer:
        customer = self.customer_repo.get_customer_by_field('id', id)
        if not customer:
            raise NotFoundError('Customer not found')
        return customer

    def _get_mold_or_404(self, id: str) -> Mold:
        mold = self.mold_repo.get_mold_by_field('id', id)
        if not mold:
            raise NotFoundError('Mold not found')
        return mold

    def _calculate_priority(
        self, delivery_date: datetime, parts: List[Part]
    ) -> PriorityEnum:
        now = datetime.now()
        days_until_delivery = (delivery_date - now).days

        if days_until_delivery <= URGENT_DAYS_THRESHOLD:
            priority_score = 4  # Urgente
        elif days_until_delivery <= HIGH_DAYS_THRESHOLD:
            priority_score = 3  # Alta
        elif days_until_delivery <= MEDIUM_DAYS_THRESHOLD:
            priority_score = 2  # Média
        else:
            priority_score = 1  # Baixa

        parts_score = self.__sum_parts_progress(parts)

        parts_not_ready = len(parts) - parts_score
        priority_score += parts_not_ready

        if priority_score >= URGENT_PRIORITY_THRESHOLD:
            return PriorityEnum.URGENT
        elif priority_score >= HIGH_PRIORITY_THRESHOLD:
            return PriorityEnum.HIGH
        elif priority_score >= MEDIUM_PRIORITY_THRESHOLD:
            return PriorityEnum.MEDIUM
        else:
            return PriorityEnum.LOW

    def _calculate_mold_progress(self, parts: List[Part]) -> float:
        total_parts = len(parts)
        completed_parts = self.__sum_parts_progress(parts)

        if total_parts == 0:
            return 0.0

        return (completed_parts / total_parts) * 100

    @staticmethod
    def _sum_parts_progress(parts: List[Part]):
        return sum(
            1
            if part.status == PartStatusEnum.COMPLETED
            else 0.5
            if part.status == PartStatusEnum.IN_PROGRESS
            else 0.0
            for part in parts
        )

    @staticmethod
    def _update_mold_fields(payload: MoldBase, target: Mold) -> Mold:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key):
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.mold_repo.get_mold_by_field('name', name, exclude_id=exclude_id):
            raise DataConflictError(f"A mold with name '{name}' already exists.")
