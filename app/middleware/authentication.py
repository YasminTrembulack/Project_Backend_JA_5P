from fastapi import status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from loguru import logger
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import security
from app.db.database import get_session
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import (
    APIException,
    AuthTokenMissingError,
    InvalidTokenError,
)
from app.types.exceptions import (
    APIException,
    AuthTokenMissingError,
    InvalidTokenError,
)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def dispatch(request, call_next):
        if request.url.path.startswith('/api/login'):
            return await call_next(request)
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise AuthTokenMissingError('Authentication token is missing')

            token = auth_header.split(' ')[1].strip()

            payload = security.verify_access_token(token)
            user_id = payload.get('user_id')

            session: Session = next(get_session())
            try:
                repo = UserRepository(session)
                user = repo.get_user_by_id(user_id)
            finally:
                session.close()

            if user is None:
                raise InvalidTokenError()
            request.state.user = user

        except APIException as e:
            logger.error(f'{e.__class__.__name__}: {e.message}')
            user_id = payload.get('user_id')

            session: Session = next(get_session())
            try:
                repo = UserRepository(session)
                user = repo.get_user_by_id(user_id)
            finally:
                session.close()

            if user is None:
                raise InvalidTokenError()
            request.state.user = user

        except APIException as e:
            logger.error(f'{e.__class__.__name__}: {e.message}')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': f'{e.message}'},
            )
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e.message}')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Unexpected error while verifying token.'},
            )
        return await call_next(request)
