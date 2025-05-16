from fastapi import status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import security
from app.db.database import get_session
from app.repositories.user_repositorie import UserRepository
from app.types import (
    APIException,
    AuthTokenMissingError,
    InvalidTokenError,
)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def dispatch(request, call_next):
        if request.method == 'OPTIONS' or request.url.path.startswith('/api/login'):
            return await call_next(request)
        try:
            auth_header = request.headers.get('Authorization')
            access_token = None
            refresh_token = None

            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1].strip()
            else:
                refresh_token = request.cookies.get('refresh_token')
                print(f'REFRESH TOKEN: {refresh_token}')
                if not refresh_token:
                    raise AuthTokenMissingError('Authentication token is missing')

            if refresh_token:
                payload = security.verify_refresh_token(refresh_token)
            else:
                payload = security.verify_access_token(access_token)

            user_id = payload.get('id')

            if not user_id:
                raise InvalidTokenError('User ID not found in token.')

            session: Session = next(get_session())  # Criar a sessão
            try:
                repo = UserRepository(session)
                user = repo.get_user_by_field('id', user_id)
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
            logger.error(f'{e.__class__.__name__}: {str(e)}')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Unexpected error while verifying token.'},
            )
        return await call_next(request)
