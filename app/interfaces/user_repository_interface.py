from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.user import User
from app.types.schemas import UserPayload


class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserPayload) -> User:
        pass

    @abstractmethod
    def get_user_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[User], int]:
        pass

    @abstractmethod
    def delete_user(self, user: User) -> None:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def restore_user(self, user: User) -> User:
        pass
