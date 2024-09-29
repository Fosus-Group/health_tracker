from datetime import datetime

from pydantic import BaseModel, Field


class UploadStatsSchema(BaseModel):
    """Схема для загрузки данных о статистике пользователя."""

    water_amount: float | None = Field(
        None,
        description="Вода.",
        example=[3.2]
    )
    steps_amount: int | None = Field(
        None,
        description="Количество шагов",
        example=[9783]
    )
    weight_amount: float | None = Field(
        None,
        description="Вес",
        example=[89.5]
    )
    recorded_at: datetime = Field(
        ...,
        description="Дата в которую было записаны данные.",
        example=["2020-05-01"]
    )


class StatRecordSchema(BaseModel):
    """Схема для возврата записи статистики."""

    recorded_at: datetime = Field(
        ...,
        description="Дата записи данных",
        example="2020-05-01T00:00:00Z"
    )
    value: float = Field(
        ...,
        description="Значение записи (вес, количество воды или шаги)",
        example=89.5
    )
