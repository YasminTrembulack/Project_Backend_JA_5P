from datetime import date, datetime, time
from typing import List, Tuple

import pytz
from dateutil import parser
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.core.settings import Settings
from app.models.customer import Customer
from app.models.mold import Mold
from app.repositories.customer_repositorie import CustomerRepository
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.part_repositorie import PartRepository
from app.services.filter_service import FilterService
from app.services.progress_service import ProgressService
from app.types.base import BaseQueryParams, MoldBase
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.payload import (
    MoldPayload,
    MoldUpdatePayload,
    PaginationParams,
)
from app.types.response import (
    CustomerResponse,
    OperationAssociationResponse,
    PartResponse,
    UserResponse,
)


class MoldService:
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.mold_repo = MoldRepository(db)
        self.part_repo = PartRepository(db)
        self.filter_service = FilterService()
        self.progress_service = ProgressService(self.mold_repo, self.part_repo)

    def mold_register(self, payload: MoldPayload) -> Mold:
        if payload.customer_id:
            self._get_customer_or_404(payload.customer_id)
        payload.delivery_date = self._validate_delivery_date(payload.delivery_date)
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.mold_repo.total_molds(True) + 1
            payload.name = str(new_name)
        return self.mold_repo.create_mold(payload)

    def get_all_molds(self, query: BaseQueryParams) -> Tuple[List[Mold], int]:
        order_attr = getattr(Mold, query.order_by, None)

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
            'mold', query.field, query.value
        )
        
        molds, total_molds = self.mold_repo.get_all_molds_paginated(
            pagination_params, order, filters, joins
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
        new_delivery_date = updated_data.get('delivery_date', mold.delivery_date)
        self._validate_name_uniqueness(new_name, mold.id)

        its_a_new_delivery_date = True if 'delivery_date' in updated_data else False

        if its_a_new_delivery_date:
            payload.delivery_date = self._validate_delivery_date(new_delivery_date)
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

    @staticmethod
    def configure_associations_response(mold: Mold, associations: List[str]) -> dict:
        def _load_customer():
            return CustomerResponse.model_validate(mold.customer.to_dict())

        def _load_created_by():
            return UserResponse.model_validate(mold.created_by.to_dict())

        def _load_mold_parts():
            return [
                PartResponse.model_validate(p.to_dict()) for p in mold.mold_parts
            ]

        def _load_operation_associations():
            return [
                OperationAssociationResponse.model_validate(op.to_dict())
                for op in mold.operation_associations
            ]

        loaders = {
            'customer': _load_customer,
            'created_by': _load_created_by,
            'mold_parts': _load_mold_parts,
            'operation_associations': _load_operation_associations,
        }

        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(mold, key, None) is not None
        }

    def _calculate_priority(self, mold: Mold) -> Mold:
        # if mold.priority_updated_at != date.today(): #TODO ADICIONAR ISSO DEPOIS
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

    @staticmethod
    def _validate_delivery_date(dd):
        if dd is None:
            return dd

        timezone = pytz.timezone(Settings().TZ)
        current_time = datetime.now(timezone)

        if isinstance(dd, str):
            try:
                dd = parser.parse(dd)
            except (ValueError, TypeError):
                raise InvalidFieldError('Invalid date format. Use YYYY-MM-DD.')

        if isinstance(dd, date) and not isinstance(dd, datetime):
            value_naive = datetime.combine(dd, time(23, 59, 59))
            dd = timezone.localize(value_naive)

        elif isinstance(dd, datetime) and dd.tzinfo is None:
            dd = timezone.localize(dd)

        elif isinstance(dd, datetime) and dd.tzinfo is not None:
            dd = dd.astimezone(timezone)

        if dd < current_time:
            raise InvalidFieldError('Delivery date must be in the future.')

        return dd
