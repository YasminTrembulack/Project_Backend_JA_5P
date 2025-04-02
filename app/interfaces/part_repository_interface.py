from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.part import Part
from app.types.schemas import PartPayload


class IPartRepository(ABC):
    @abstractmethod
    def create_part(self, part: PartPayload) -> Part:
        pass

    @abstractmethod
    def get_part_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Part]:
        pass

    @abstractmethod
    def get_all_parts_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Part], int]:
        pass

    @abstractmethod
    def delete_part(self, part: Part) -> None:
        pass

    @abstractmethod
    def update_part(self, part: Part) -> Part:
        pass

    @abstractmethod
    def restore_part(self, part: Part) -> Part:
        pass

    @abstractmethod
    def total_parts(self, include_inactive: Optional[bool] = False) -> int:
        pass
