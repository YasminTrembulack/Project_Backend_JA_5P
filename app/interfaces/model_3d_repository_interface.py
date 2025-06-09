from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.model_3d import Model3D
from app.types.payload import Model3DPayload


class IModel3DRepository(ABC):
    @abstractmethod
    def create_model_3d(self, model_3d: Model3DPayload) -> Model3D:
        pass

    @abstractmethod
    def get_model_3d_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Model3D]:
        pass

    @abstractmethod
    def get_all_model_3ds_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Model3D], int]:
        pass

    @abstractmethod
    def delete_model_3d(self, model_3d: Model3D) -> None:
        pass

    @abstractmethod
    def update_model_3d(self, model_3d: Model3D) -> Model3D:
        pass

    @abstractmethod
    def restore_model_3d(self, model_3d: Model3D) -> Model3D:
        pass

    @abstractmethod
    def total_model_3ds(self, include_inactive: Optional[bool] = False) -> int:
        pass
