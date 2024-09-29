from sqlalchemy.ext.asyncio import AsyncSession

from repositories.stats_repository import StatsRepository
from datetime import datetime
from core.config import Settings, get_app_settings
from schemas.stats import UploadStatsSchema, StatRecordSchema

app_settings: Settings = get_app_settings()


class StatsService:
    """Сервис для работы со статистикой пользователей."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.stats_repository = StatsRepository(db_session=db_session)

    async def upload_user_stats(self, phone_number: str, stats_data: UploadStatsSchema) -> None:
        """Метод для добавления записи о статистике пользователя."""
        await self.stats_repository.insert_stats_data(
            phone_number=phone_number,
            stats_data=stats_data.dict(),
        )

    async def get_user_stats(
        self,
        phone_number: str,
        stat_type: str,
        limit: int,
        offset: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[StatRecordSchema] | None:
        """Получение статистики пользователя с поддержкой пагинации и фильтрации по дате."""
        user = await self.stats_repository.get_user_by_phone(phone_number)
        if not user:
            raise ValueError("Пользователь не найден.")

        returned_stats: list[dict] = []

        if stat_type == "weight":
            records = await self.stats_repository.get_weight_records(
                user.id, limit, offset, start_date, end_date
            )
            for record in records:
                returned_stats.append(
                    {
                        "value": record.weight,
                        "recorded_at": record.recorded_at,
                    }
                )
        elif stat_type == "water":
            records = await self.stats_repository.get_water_records(
                user.id, limit, offset, start_date, end_date
            )
            for record in records:
                returned_stats.append(
                    {
                        "value": record.water_amount,
                        "recorded_at": record.recorded_at,
                    }
                )
        elif stat_type == "steps":
            records = await self.stats_repository.get_step_records(
                user.id, limit, offset, start_date, end_date
            )
            for record in records:
                returned_stats.append(
                    {
                        "value": record.steps_count,
                        "recorded_at": record.recorded_at,
                    }
                )
        if returned_stats:
            return [StatRecordSchema.model_validate(stat) for stat in returned_stats]
        return None
