from fastapi import APIRouter

from endpoints import health

routers = APIRouter()

routers.include_router(health.router)
