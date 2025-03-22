from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.settings import Settings
from app.db.database import run_migrations, test_connection
from app.middleware.authentication import AuthenticationMiddleware
from app.routes.auth_route import router as auth_router
from app.routes.ping import router as ping_route
from app.routes.user_route import router as user_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    test_connection()
    if not Settings().LOCAL_ENV:
        run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix=Settings().API_PREFIX)
app.include_router(ping_route, prefix=Settings().API_PREFIX)
app.include_router(auth_router, prefix=Settings().API_PREFIX)

# app.add_middleware(AuthenticationMiddleware)
