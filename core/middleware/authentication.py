from uuid import UUID

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware

# from jose import ExpiredSignatureError, JWTError
from core.db.database import get_session
from core.models.user import User
from core.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class AuthenticationMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def dispatch(request, call_next):
        if request.url.path.startswith('/api/login'):
            return await call_next(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail='Authentication token is missing'
            )

        token = auth_header.split(' ')[1].strip()

        try:
            payload = jwt.decode(
                token,
                Settings().SECRET_KEY,
                algorithms=[Settings().ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired. Please log in again."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token. Authentication failed."
            )

        user_id = payload.get('user_id')
        db = next(get_session())

        try:
            user = db.query(User).filter(User.id == UUID(user_id)).first()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while querying the database: {str(e)}"
            )
        finally:
            db.close()

        if user is None:
            raise HTTPException(status_code=404, detail='Invalid access token')

        return await call_next(request)
