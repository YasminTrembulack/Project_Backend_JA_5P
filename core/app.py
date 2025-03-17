from fastapi import FastAPI

from core.routes.ping import router as ping_route
from core.routes.user import router as user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(ping_route)
