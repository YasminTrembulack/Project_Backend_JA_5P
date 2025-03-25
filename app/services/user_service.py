from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import DataConflictError
from app.types.schemas import UserPayload


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def user_register(self, user: UserPayload) -> User:
        user_found = self.user_repo.get_user_by_field('email', user.email)
        user_found = self.user_repo.get_user_by_field(
            'registration_number', user.registration_number
        )
        if user_found:
            raise DataConflictError(
                'Email alredy in use.'
                if user.email == user_found.email
                else 'Registration number alredy in use.'
            )
        return self.user_repo.create_user(user)

    def get_all_users(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[User], int]:
        offset = (page - 1) * limit
        order = (
            desc(getattr(User, order_by)) if desc_order else getattr(User, order_by)
        )
        return self.user_repo.get_all_users_paginated(offset, limit, order)
