from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.mold import Mold
from app.types.schemas import MoldPayload


class IMoldRepository(ABC):
    @abstractmethod
    def create_mold(self, mold: MoldPayload) -> Mold:
        pass

    @abstractmethod
    def get_mold_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Mold]:
        pass

    @abstractmethod
    def get_all_molds_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        parts: Optional[bool] = False,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Mold], int]:
        pass

    @abstractmethod
    def delete_mold(self, mold: Mold) -> None:
        pass

    @abstractmethod
    def update_mold(self, mold: Mold) -> Mold:
        pass

    @abstractmethod
    def restore_mold(self, mold: Mold) -> Mold:
        pass

    @abstractmethod
    def total_molds(self, include_inactive: Optional[bool] = False) -> int:
        pass
