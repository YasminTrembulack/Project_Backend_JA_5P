from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core import security
from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import DataConflictError, NotFoundError
from app.types.schemas import UserPayload, UserUpdatePayload


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
        payload = payload.model_dump(exclude_unset=True)

        user = self.user_repo.get_user_by_field('id', id)
        if not user:
            raise NotFoundError('User not found')

        self._validate_unique_fields(payload, user.id)

        if 'password' in payload:
            payload.password = security.hash_password(payload.password)

        return self.user_repo.update_user(user, payload)

    def _validate_unique_fields(self, payload: dict, user_id: str):
        if 'email' in payload and self._is_field_in_use(
            'email', payload['email'], user_id
        ):
            raise DataConflictError('Email already in use.')

        if 'registration_number' in payload and self._is_field_in_use(
            'registration_number',
            payload['registration_number'],
            user_id,
        ):
            raise DataConflictError('Registration number already in use.')

    def _is_field_in_use(self, field: str, value: str, user_id: str) -> bool:
        existing_user = self.user_repo.get_user_by_field(field, value)
        return existing_user is not None and existing_user.id != user_id
