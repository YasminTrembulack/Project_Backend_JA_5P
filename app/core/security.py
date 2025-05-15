from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from passlib.context import CryptContext

from app.core.settings import Settings
from app.types.exceptions import ExpiredSignatureError, InvalidTokenError


class SecurityManager:
    def __init__(self):
        self.secret_key = Settings().SECRET_KEY
        self.algorithm = Settings().ALGORITHM
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _create_token(self, data: dict, expires_in: int, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        to_encode.update({'exp': expire, 'type': token_type})
        return jwt.encode(to_encode, self.secret_key, self.algorithm)

    def create_access_token(self, data: dict, expires_in: int = 15) -> str: #TODO expires_in 15
        return self._create_token(data, expires_in, 'access')

    def create_refresh_token(self, data: dict, expires_in: int = 60 * 24 * 7) -> str:
        return self._create_token(data, expires_in, 'refresh')

    def _verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ExpiredSignatureError('Token has expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
        return payload

    def verify_access_token(self, token: str) -> Dict:
        payload = self._verify_token(token)
        if payload.get('type') != 'access':
            raise InvalidTokenError('This is not an access token.')
        return payload

    def verify_refresh_token(self, token: str) -> Dict:
        payload = self._verify_token(token)
        if payload.get('type') != 'refresh':
            raise InvalidTokenError('This is not a refresh token.')
        return payload


security = SecurityManager()
