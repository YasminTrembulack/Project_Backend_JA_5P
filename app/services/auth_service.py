from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import security
from app.repositories.user_repositorie import UserRepository
from app.types.schemas import LoginPayload


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, user: LoginPayload):
        user_found = self.user_repo.get_user_by_email(
            user.email
        )
        if not user_found:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid email or password'
            )
        if not security.verify_password(user.password, user_found.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid email or password'
            )
        payload = {
            'user_id': str(user_found.id),
            'user_role': user_found.role
        }
        access_token = security.create_access_token(payload)
        return access_token, user_found
