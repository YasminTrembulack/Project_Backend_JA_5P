from datetime import datetime, timedelta
from http import HTTPStatus

import jwt
import pytz
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.models.user import User
from core.settings import Settings
from core.types.schemas import LoginPayload
from core.utils.crypt import crypt_context


class AuthController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def login(self, user: LoginPayload, expires_in: int = 30):
        user_found = (
            self.db_session
            .query(User)
            .filter_by(email=user.email)
            .first()
        )
        if not user_found:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid email or password'
            )
        if not crypt_context.verify(user.password, user_found.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid email or password'
            )

        expire = datetime.now(tz=pytz.UTC) + timedelta(
            minutes=expires_in
        )
        payload = {
            'user_id': str(user_found.id),
            'user_role': user_found.role,
            'exp': int(expire.timestamp()),
            # 'iat': datetime.now()
        }
        print("EXP: ", expire)
        access_token = jwt.encode(
            payload,
            Settings().SECRET_KEY,
            algorithm=Settings().ALGORITHM
        )
        return access_token, user_found
