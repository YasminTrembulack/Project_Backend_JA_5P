from fastapi import FastAPI

from core.routes.ping import router as ping_route

app = FastAPI()

app.include_router(ping_route)
