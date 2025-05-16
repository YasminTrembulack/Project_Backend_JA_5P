from sqlalchemy.orm import Session

from app.core.security import security
from app.repositories.user_repositorie import UserRepository
from app.types import InvalidCredentialsError, InvalidTokenError
from app.types import LoginPayload


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, user: LoginPayload):
        user_found = self.user_repo.get_user_by_field('email', user.email)
        if not user_found:
            raise InvalidCredentialsError('Invalid email or password')
        if not security.verify_password(user.password, user_found.password):
            raise InvalidCredentialsError('Invalid email or password')

        payload = {k: v for k, v in user_found.to_dict().items() if k != 'password'}

        access_token = security.create_access_token(payload)
        refresh_token = security.create_refresh_token({'id': user_found.id})
        return access_token, refresh_token, user_found

    def refresh_token(self, user_id: str):
        user_found = self.user_repo.get_user_by_field('id', user_id)

        if not user_found:
            raise InvalidTokenError('User not found or token is invalid.')

        payload = {k: v for k, v in user_found.to_dict().items() if k != 'password'}

        access_token = security.create_access_token(payload)
        return access_token
