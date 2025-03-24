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

    def create_access_token(self, data: dict, expires_in: int = 60) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        to_encode.update({'exp': expire})
        return jwt.encode(to_encode, self.secret_key, self.algorithm)

    def verify_access_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ExpiredSignatureError('Token has expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
        return payload


security = SecurityManager()
