from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.core.security import security
from app.interfaces.user_repository_interface import IUserRepository
from app.models.user import User
from app.types.exceptions import InvalidFieldError
from app.types.schemas import UserPayload


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserPayload) -> User:
        hashed_password = security.hash_password(user.password)
        db_user = User(
            full_name=user.full_name,
            password=hashed_password,
            email=user.email,
            registration_number=user.registration_number,
            role=user.role,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_field(self, field_name: str, value: str) -> Optional[User]:
        user_field = getattr(User, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on User model'
            )
        return self.db.query(User).filter(user_field == value).first()

    def get_all_users_paginated(
        self, offset: int, limit: int, order: UnaryExpression
    ) -> Tuple[List[User], int]:
        users = self.db.query(User).order_by(order).offset(offset).limit(limit).all()
        total_users = self.db.query(User).count()
        return users, total_users
