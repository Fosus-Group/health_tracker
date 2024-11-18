from fastapi import APIRouter

from endpoints import health, user, stats, follower

routers = APIRouter()

routers.include_router(health.router)
routers.include_router(user.router)
routers.include_router(stats.router)
routers.include_router(follower.router)
