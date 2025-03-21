from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.schemas import UserSchema


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def user_register(self, user: UserSchema) -> User:
        user_found = self.user_repo.get_user_by_email(
            user.email
        )
        if user_found:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                detail='Email alredy exists.'
            )
        return self.user_repo.create_user(user)
