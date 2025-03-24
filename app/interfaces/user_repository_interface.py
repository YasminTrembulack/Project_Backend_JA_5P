from abc import ABC, abstractmethod

from app.models.user import User
from app.types.schemas import UserPayload


class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserPayload) -> User:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> User | None:
        pass
