from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.material import Material
from app.types.schemas import MaterialPayload


class IMaterialRepository(ABC):
    @abstractmethod
    def create_material(self, material: MaterialPayload) -> Material:
        pass

    @abstractmethod
    def get_material_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Material]:
        pass

    @abstractmethod
    def get_all_materials_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Material], int]:
        pass

    @abstractmethod
    def delete_material(self, material: Material) -> None:
        pass

    @abstractmethod
    def update_material(self, material: Material) -> Material:
        pass

    @abstractmethod
    def restore_material(self, material: Material) -> Material:
        pass

    @abstractmethod
    def total_material(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        pass
