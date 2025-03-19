from fastapi import FastAPI

from core.middleware.authentication import AuthenticationMiddleware
from core.routes.auth_route import router as auth_router
from core.routes.ping import router as ping_route
from core.routes.user_route import router as user_router

app = FastAPI()
PREFIX = '/api'

app.include_router(user_router, prefix=PREFIX)
app.include_router(ping_route, prefix=PREFIX)
app.include_router(auth_router, prefix=PREFIX)


app.add_middleware(AuthenticationMiddleware)
