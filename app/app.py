from fastapi import FastAPI

from app.middleware.authentication import AuthenticationMiddleware
from app.routes.auth_route import router as auth_router
from app.routes.ping import router as ping_route
from app.routes.user_route import router as user_router

app = FastAPI()
PREFIX = '/api'

app.include_router(user_router, prefix=PREFIX)
app.include_router(ping_route, prefix=PREFIX)
app.include_router(auth_router, prefix=PREFIX)


app.add_middleware(AuthenticationMiddleware)
