from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import security
from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import DataConflictError, InvalidFieldError, NotFoundError
from app.types.schemas import UserBase, UserPayload, UserUpdatePayload


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def user_register(self, payload: UserPayload) -> User:
        self._validate_user_uniqueness(payload.email, payload.registration_number)
        payload.password = security.hash_password(payload.password)
        return self.user_repo.create_user(payload)

    def get_all_users(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[User], int]:
        if not hasattr(User, order_by):
            raise InvalidFieldError(f'Field {order_by} does not exist on User model')
        offset = (page - 1) * limit
        order = (
            desc(getattr(User, order_by)) if desc_order else getattr(User, order_by)
        )
        return self.user_repo.get_all_users_paginated(offset, limit, order)

    def delete_user(self, id: str) -> None:
        user = self._get_user_or_404(id)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        user.email = f'deleted_{timestamp}_{user.email}'
        user.registration_number = f'deleted_{timestamp}_{user.registration_number}'
        return self.user_repo.delete_user(user)

    def update_user(self, id: str, payload: UserUpdatePayload) -> User:
        user = self._get_user_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_email = updated_data.get('email', user.full_name)
        new_registration_number = updated_data.get(
            'registration_number', user.registration_number
        )

        if new_email or new_registration_number:
            self._validate_user_uniqueness(
                new_email, new_registration_number, user.id
            )

        if payload.password:
            payload.password = security.hash_password(payload.password)

        updated_user = self._update_user_fields(payload, user)
        return self.user_repo.update_user(updated_user)

    def get_user(self, id: str) -> User:
        return self._get_user_or_404(id)

    def _validate_user_uniqueness(
        self, email: str, reg_number: str, exclude_id: str = None
    ) -> None:
        if self.user_repo.get_user_by_field('email', email, exclude_id):
            raise DataConflictError(f"A user with email '{email}' already exists.")

        if self.user_repo.get_user_by_field(
            'registration_number', reg_number, exclude_id
        ):
            raise DataConflictError(
                f"A user with registration number '{reg_number}' already exists."
            )

    def _get_user_or_404(self, id: str) -> User:
        user = self.user_repo.get_user_by_field('id', id)
        if not user:
            raise NotFoundError('User not found')
        return user

    @staticmethod
    def _update_user_fields(payload: UserBase, target: User) -> User:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target
