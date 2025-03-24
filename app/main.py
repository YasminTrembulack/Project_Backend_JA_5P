from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from starlette.middleware.cors import CORSMiddleware

from app.core.settings import Settings
from app.db.database import run_migrations, test_connection
from app.middleware.authentication import AuthenticationMiddleware
from app.middleware.erro_handling import create_exception_handler
from app.routes.auth_route import router as auth_router
from app.routes.ping import router as ping_route
from app.routes.user_route import router as user_router
from app.types.exceptions import (
    DataConflictError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    PermissionDeniedError,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    test_connection()
    if not Settings().LOCAL_ENV:
        run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix=Settings().API_PREFIX)
app.include_router(ping_route, prefix=Settings().API_PREFIX)
app.include_router(auth_router, prefix=Settings().API_PREFIX)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_middleware(AuthenticationMiddleware)

app.add_exception_handler(
    exc_class_or_status_code=PermissionDeniedError,
    handler=create_exception_handler(status.HTTP_403_FORBIDDEN, 'Permission denied'),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidCredentialsError,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, 'Invalid credentials'
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=NotAuthenticatedError,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, 'Not authenticated'
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=DataConflictError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, 'Data conflict error'
    ),
)
