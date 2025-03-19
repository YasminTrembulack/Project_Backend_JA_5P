from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.models.user import User
from core.types.schemas import UserSchema
from core.utils.crypt import crypt_context


class UserController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def user_register(self, user: UserSchema) -> User:
        user_found = (
            self.db_session
            .query(User)
            .filter_by(email=user.email)
            .first()
        )
        if user_found:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                detail='Email alredy exists.'
            )
        hashed_password = crypt_context.hash(user.password)
        db_user = User(
            full_name=user.full_name,
            password=hashed_password,
            email=user.email,
            role=user.role
        )

        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        return db_user
