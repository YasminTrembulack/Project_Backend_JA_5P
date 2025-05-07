from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.material import MaterialPart
from app.types.schemas import MaterialPartPayload


class IMaterialPartRepository(ABC):
    @abstractmethod
    def create_material_part(
        self, material_part: MaterialPartPayload
    ) -> MaterialPart:
        pass

    @abstractmethod
    def get_material_part_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[MaterialPart]:
        pass

    @abstractmethod
    def get_all_material_parts_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
        item_id: Optional[str] = None,
    ) -> Tuple[List[MaterialPart], int]:
        pass

    @abstractmethod
    def delete_material_part(self, material_part: MaterialPart) -> None:
        pass

    @abstractmethod
    def update_material_part(self, material_part: MaterialPart) -> MaterialPart:
        pass

    @abstractmethod
    def restore_material_part(self, material_part: MaterialPart) -> MaterialPart:
        pass

    @abstractmethod
    def get_by_part_and_material(
        self, part_id: str, material_id: str, exclude_id: Optional[str] = None
    ) -> MaterialPart:
        pass

    @abstractmethod
    def get_by_id_and_status(
        self, part_id: str, status: str, exclude_id: Optional[str] = None
    ) -> Optional[MaterialPart]:
        pass
