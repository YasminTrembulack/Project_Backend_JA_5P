from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import security
from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import DataConflictError, NotFoundError
from app.types.schemas import UserPayload, UserUpdatePayload


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def user_register(self, user: UserPayload) -> User:
        self._validate_unique_fields(user.model_dump())
        user.password = security.hash_password(user.password)
        return self.user_repo.create_user(user)

    def get_all_users(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[User], int]:
        offset = (page - 1) * limit
        order = (
            desc(getattr(User, order_by)) if desc_order else getattr(User, order_by)
        )
        return self.user_repo.get_all_users_paginated(offset, limit, order)

    def delete_user(self, id: str) -> None:
        user = self.user_repo.get_user_by_field('id', id)
        if not user:
            raise NotFoundError('User not found')
        return self.user_repo.delete_user(user)

    def update_user(self, id: str, payload: UserUpdatePayload) -> User:
        user = self.user_repo.get_user_by_field('id', id)
        if not user:
            raise NotFoundError('User not found')

        self._validate_unique_fields(payload.model_dump(), user.id)

        if payload.password:
            payload.password = security.hash_password(payload.password)

        payload = payload.model_dump(exclude_unset=True)
        return self.user_repo.update_user(user, payload)

    def get_user(self, id: str) -> User:
        user = self.user_repo.get_user_by_field('id', id)
        if not user:
            raise NotFoundError('User not found')
        return user

    def _validate_unique_fields(self, payload: dict, user_id: str = None):
        if payload.get('email', False) and self._is_field_in_use(
            'email', payload.get('email'), user_id
        ):
            raise DataConflictError('Email already in use.')

        if payload.get('registration_number', False) and self._is_field_in_use(
            'registration_number',
            payload.get('registration_number'),
            user_id,
        ):
            raise DataConflictError('Registration number already in use.')

    def _is_field_in_use(self, field: str, value: str, user_id: str) -> bool:
        existing_user = self.user_repo.get_user_by_field(field, value)
        if user_id:
            return existing_user is not None and existing_user.id != user_id
        return existing_user is not None
