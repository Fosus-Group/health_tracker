from fastapi import APIRouter

from endpoints import health, user

routers = APIRouter()

routers.include_router(health.router)
routers.include_router(user.router)
