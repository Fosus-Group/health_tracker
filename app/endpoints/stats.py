from fastapi import APIRouter, status, Depends, HTTPException, Query
from schemas.user import BaseResponseSchema, UserSchema
from schemas.problem import ProblemDetail
from schemas.stats import UploadStatsSchema, StatRecordSchema
from core.dependencies import get_current_user, get_stats_service
from services.stats_service import StatsService
from datetime import datetime

router = APIRouter(prefix="/stats", tags=["Статистика."])


@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
    summary="Внесение данных пользователя.",
    responses={
        200: {
            "model": BaseResponseSchema,
            "description": "Информация успешно получена.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        422: {
            "description": "Некорректные данные.",
            "model": ProblemDetail,
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def upload_stats(
    stats_data: UploadStatsSchema,
    user: UserSchema = Depends(get_current_user),
    stats_service: StatsService = Depends(get_stats_service),
) -> BaseResponseSchema:
    """Эндпоинт для отправки статистики пользователя."""
    if not stats_data.steps_amount and not stats_data.water_amount and not stats_data.weight_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Не введены данные."
        )

    try:
        await stats_service.upload_user_stats(
            phone_number=user.phone_number,
            stats_data=stats_data,
        )
        return BaseResponseSchema(success=True)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректные данные статистики."
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[StatRecordSchema],
    summary="Получение статистики пользователя.",
    responses={
        200: {
            "model": list[StatRecordSchema],
            "description": "Информация успешно получена.",
        },
        400: {
            "model": ProblemDetail,
            "description": "Некорректный параметр запроса.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        404: {
            "description": "Записи не найдены.",
            "model": ProblemDetail,
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def get_stats(
    arg: str,
    limit: int = Query(10, ge=1, le=100, description="Количество записей для получения."),
    offset: int = Query(0, ge=0, description="Смещение для пагинации."),
    start_date: datetime | None = Query(None, description="Дата начала периода."),
    end_date: datetime | None = Query(None, description="Дата конца периода."),
    user: UserSchema = Depends(get_current_user),
    stats_service: StatsService = Depends(get_stats_service),
) -> list[StatRecordSchema]:
    """Эндпоинт для получения статистики пользователя (вес, вода или шаги) с фильтрацией по дате и пагинацией."""
    try:
        if arg not in ["weight", "water", "steps"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный параметр. Допустимые значения: 'weight', 'water', 'steps'."
            )

        stats: list[StatRecordSchema] | None = await stats_service.get_user_stats(
            phone_number=user.phone_number,
            stat_type=arg,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Записи не найдены."
            )

        return stats

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
