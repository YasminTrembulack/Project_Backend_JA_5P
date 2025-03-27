from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.user_repository_interface import IUserRepository
from app.models.user import User
from app.types.exceptions import InvalidFieldError
from app.types.schemas import UserPayload


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserPayload) -> User:
        db_user = User(
            full_name=user.full_name,
            password=user.password,
            email=user.email,
            registration_number=user.registration_number,
            role=user.role,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[User]:
        user_field = getattr(User, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on User model'
            )
        query = self.db.query(User).filter(user_field == value)
        if not include_inactive:
            query = query.filter(User.is_active.is_(True))
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first()

    def get_all_users_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[User], int]:
        query = self.db.query(User)

        if not include_inactive:
            query = query.filter(User.is_active.is_(True))

        users = query.order_by(order).offset(offset).limit(limit).all()
        total_users = query.count()

        return users, total_users

    def delete_user(self, user: User) -> None:
        user.is_active = False
        user.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def restore_user(self, user: User) -> User:
        user.is_active = True
        user.archived_at = None
        self.db.commit()
        self.db.refresh(user)
        return user
