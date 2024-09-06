from typing import Annotated

from core.dependencies import get_db
from fastapi import APIRouter, Depends, status
from schemas.liveness import LivenessReadinessSchema, LivenessReadinessStatus
from schemas.problem import ProblemDetail
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/health", tags=["Доступность и читаемость"])


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    response_model=LivenessReadinessSchema,
    summary="Проверка доступности приложения",
    responses={
        200: {
            "model": LivenessReadinessSchema,
            "description": "Приложение доступно и работает.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def liveness() -> LivenessReadinessSchema:
    """Эндпоинт для проверки на доступность приложения."""
    return LivenessReadinessSchema(status=LivenessReadinessStatus.ALIVE)


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    response_model=LivenessReadinessSchema,
    summary="Проверка доступности базы данных на чтение.",
    responses={
        200: {
            "model": LivenessReadinessSchema,
            "description": "Статус доступности к базе данных.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def readiness(db: Annotated[Session, Depends(get_db)]) -> LivenessReadinessSchema:
    """Эндпоинт для проверки на читаемость из базы данных."""
    try:
        # нельзя делать запросы в бд из эндпоинта, такие вещи происходят на самом нижнем слое в репозитории
        # здесь только для исключения так как эндпоинт просто проверяет доступность бд
        await db.execute(select(1))  # type: ignore
        return LivenessReadinessSchema(status=LivenessReadinessStatus.READY)
    except Exception:  # noqa: BLE001
        return LivenessReadinessSchema(status=LivenessReadinessStatus.ERROR)
