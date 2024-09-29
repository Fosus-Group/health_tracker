from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import (
    User,
    WaterIntakeRecord,
    WeightRecord,
    StepRecord,
)
from datetime import datetime


class StatsRepository:
    """Репозиторий для работы со статистикой пользователей."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def insert_stats_data(self, phone_number: str, stats_data: dict) -> None:
        """Метод для вставки в бд данных о статистике пользователя."""
        user = await self.get_user_by_phone(phone_number)
        if not user:
            raise ValueError("Пользователь с данным номером телефона не найден.")

        if not user:
            raise ValueError("Пользователь с данным номером телефона не найден.")

        if stats_data.get("steps_amount", None):
            new_steps = StepRecord(
                user_id=user.id,
                steps_count=stats_data["steps_amount"],
                recorded_at=stats_data["recorded_at"]
            )
            self.db_session.add(new_steps)

        if stats_data.get("weight_amount", None):
            new_weight = WeightRecord(
                user_id=user.id,
                weight=stats_data["weight_amount"],
                recorded_at=stats_data["recorded_at"]
            )
            self.db_session.add(new_weight)

        if stats_data.get("water_amount", None):
            new_water = WaterIntakeRecord(
                user_id=user.id,
                water_amount=stats_data["water_amount"],
                recorded_at=stats_data["recorded_at"]
            )
            self.db_session.add(new_water)

        await self.db_session.commit()
        await self.db_session.refresh(user)

    async def get_user_by_phone(self, phone_number: str) -> User | None:
        """Получение пользователя по номеру телефона."""
        statement = select(User).where(User.phone_number == phone_number)
        result = await self.db_session.execute(statement)
        return result.scalars().one_or_none()

    async def get_weight_records(
        self,
        user_id: str,
        limit: int,
        offset: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[WeightRecord]:
        """Получение записей о весе пользователя с поддержкой фильтрации по дате и пагинации."""
        statement = select(WeightRecord).where(WeightRecord.user_id == user_id)

        if start_date:
            statement = statement.where(WeightRecord.recorded_at >= start_date)
        if end_date:
            statement = statement.where(WeightRecord.recorded_at <= end_date)

        statement = statement.limit(limit).offset(offset)
        result = await self.db_session.execute(statement)
        return list(result.scalars().all())

    async def get_water_records(
        self,
        user_id: str,
        limit: int,
        offset: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[WaterIntakeRecord]:
        """Получение записей о воде пользователя с поддержкой фильтрации по дате и пагинации."""
        statement = select(WaterIntakeRecord).where(WaterIntakeRecord.user_id == user_id)

        if start_date:
            statement = statement.where(WaterIntakeRecord.recorded_at >= start_date)
        if end_date:
            statement = statement.where(WaterIntakeRecord.recorded_at <= end_date)

        statement = statement.limit(limit).offset(offset)
        result = await self.db_session.execute(statement)
        return list(result.scalars().all())

    async def get_step_records(
        self,
        user_id: str,
        limit: int,
        offset: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[StepRecord]:
        """Получение записей о шагах пользователя с поддержкой фильтрации по дате и пагинации."""
        statement = select(StepRecord).where(StepRecord.user_id == user_id)

        if start_date:
            statement = statement.where(StepRecord.recorded_at >= start_date)
        if end_date:
            statement = statement.where(StepRecord.recorded_at <= end_date)

        statement = statement.limit(limit).offset(offset)
        result = await self.db_session.execute(statement)
        return list(result.scalars().all())
