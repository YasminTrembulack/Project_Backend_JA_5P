from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models.model_3d import Model3D
from app.repositories.model_3d_repositorie import Model3DRepository
from app.services.filter_service import FilterService
from app.types.base import BaseQueryParams, Model3DBase
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    InvalidLeadTimeError,
    NotFoundError,
)
from app.types.payload import (
    Model3DPayload,
    Model3DUpdatePayload,
    PaginationParams,
)

class Model3DService:
    def __init__(self, db: Session):
        self.model_3d_repo = Model3DRepository(db)
        self.filter_service = FilterService()

    def model_3d_register(self, payload: Model3DPayload) -> Model3D:
        ...
        # if payload.name:
        #     self._validate_name_uniqueness(payload.name)
        # else:
        #     new_name = self.model_3d_repo.total_model_3ds(True) + 1
        #     payload.name = str(new_name)
        # if not self._validate_lead_time(payload.lead_time):
        #     raise InvalidLeadTimeError(
        #         f"Invalid lead time format. Received: '{payload.lead_time}'"
        #     )
        # return self.model_3d_repo.create_model_3d(payload)

    def get_all_model_3ds(self,  query: BaseQueryParams) -> Tuple[List[Model3D], int]:
        ...
        # order_attr = getattr(Model3D, query.order_by, None)
        
        # if not isinstance(order_attr, InstrumentedAttribute):
        #     raise InvalidFieldError(
        #         f'Field {query.order_by} does not exist on Model3D model'
        #     )
        # offset = (query.page - 1) * query.limit
        # order = desc(order_attr) if query.desc_order else order_attr
        
        # pagination_params = PaginationParams(
        #     offset=offset,
        #     limit=query.limit,
        # )

        # filters, joins = self.filter_service.build_filter(
        #     'model_3d', query.field, query.value
        # )
        
        # return self.model_3d_repo.get_all_model_3ds_paginated(
        #     pagination_params, order, filters, joins
        # )

    def delete_model_3d(self, id: str) -> None:
        ...
        # model_3d = self._get_model_3d_or_404(id)
        # timestamp = int(datetime.now(timezone.utc).timestamp())
        # model_3d.name = f'deleted_{timestamp}_{model_3d.name}'
        # return self.model_3d_repo.delete_model_3d(model_3d)

    def update_model_3d(self, id: str, payload: Model3DUpdatePayload) -> Model3D:
        ...
        # model_3d = self._get_model_3d_or_404(id)
        # updated_data = payload.model_dump(exclude_unset=True)

        # new_name = updated_data.get('name', model_3d.name)

        # self._validate_name_uniqueness(new_name, id)

        # updated_model_3d = self._update_model_3d_fields(payload, model_3d)
        # return self.model_3d_repo.update_model_3d(updated_model_3d)

    def get_model_3d(self, id: str) -> Model3D:
        ...
        # return self._get_model_3d_or_404(id)

    def _get_model_3d_or_404(self, id: str) -> Model3D:
        ...
        # model_3d = self.model_3d_repo.get_model_3d_by_field('id', id)
        # if not model_3d:
        #     raise NotFoundError('Model3D not found')
        # return model_3d

    @staticmethod
    def _update_model_3d_fields(payload: Model3DBase, target: Model3D) -> Model3D:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.model_3d_repo.get_model_3d_by_field(
            'name', name, exclude_id=exclude_id
        ):
            raise DataConflictError(f"A model_3d with name '{name}' already exists.")
