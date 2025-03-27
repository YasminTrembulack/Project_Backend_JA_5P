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
        inactive_duplicate = self._get_or_validate_user_uniqueness(
            payload.email, payload.registration_number
        )
        payload.password = security.hash_password(payload.password)
        if not inactive_duplicate:
            return self.user_repo.create_user(payload)
        update_user = self._update_user_fields(payload, inactive_duplicate)
        return self.user_repo.restore_user(update_user)
        

    def get_all_users(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[User], int]:
        if not hasattr(User, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on User model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(User, order_by)) if desc_order else getattr(User, order_by)
        )
        return self.user_repo.get_all_users_paginated(offset, limit, order)

    def delete_user(self, id: str) -> None:
        user = self._get_user_or_404(id)
        return self.user_repo.delete_user(user)

    def update_user(self, id: str, payload: UserUpdatePayload) -> User:
        user = self._get_user_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_email = updated_data.get('email', user.full_name)
        new_registration_number = updated_data.get(
            'registration_number', user.registration_number)
        
        inactive_duplicate = self._get_or_validate_user_uniqueness(
            new_email, new_registration_number, user.id
        )

        if payload.password:
            payload.password = security.hash_password(payload.password)
        
        if inactive_duplicate:
            self.user_repo.delete_user(user)
            return self.user_repo.restore_user(inactive_duplicate)
        
        updated_user = self._update_user_fields(payload, user)
        return self.user_repo.update_user(updated_user)

    def get_user(self, id: str) -> User:
        return self._get_user_or_404(id)

    def _is_field_in_use(self, field: str, value: str, user_id: str) -> bool:
        existing_user = self.user_repo.get_user_by_field(field, value)
        if user_id:
            return existing_user is not None and existing_user.id != user_id
        return existing_user is not None

    def _get_or_validate_user_uniqueness(
        self, email: str, registration_number: str, exclude_id: str = None
    ) -> User | None:
        user_with_email = self.user_repo.get_user_by_field(
            'email', email, exclude_id=exclude_id, include_inactive=True
        )
        user_with_rn = self.user_repo.get_user_by_field(
            'registration_number',
            registration_number,
            exclude_id=exclude_id,
            include_inactive=True
        )

        if user_with_email and user_with_email.is_active:
            raise DataConflictError(f"A user with email '{email}' already exists.")
        
        if user_with_rn and user_with_rn.is_active:
            raise DataConflictError(
                f"A user with registration number \
                '{registration_number}' already exists."
            )
        
        if user_with_email and not user_with_email.is_active:
            if user_with_rn and not user_with_rn.is_active:
                if user_with_email.id != user_with_rn.id:
                    raise DataConflictError(
                        f"Both email '{email}' and registration number \
                        '{registration_number}' are in use by different inactive \
                        customers."
                    )
                return user_with_email

        if user_with_rn and not user_with_rn.is_active:
            return user_with_rn 
        
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