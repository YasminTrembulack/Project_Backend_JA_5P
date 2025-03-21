
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import security
from app.db.database import get_session
from app.repositories.user_repositorie import UserRepository


class AuthenticationMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def dispatch(request, call_next):
        if request.url.path.startswith('/api/login'):
            return await call_next(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication token is missing"}
            )

        token = auth_header.split(" ")[1].strip()

        try:
            payload = security.verify_access_token(token)
            user_id = payload.get("user_id")
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"Invalid or expired token"}
            )

        with next(get_session()) as db:
            repo = UserRepository(db)
            user = repo.get_user_by_id(user_id)

        if user is None:
            return JSONResponse(
                status_code=404,
                content={"detail": 'Invalid access token'}
            )
        return await call_next(request)
