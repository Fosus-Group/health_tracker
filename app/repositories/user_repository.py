from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete
from sqlalchemy.orm import selectinload
from models.user import PhoneVerification, User, WaterIntakeRecord, WeightRecord, StepRecord
import uuid


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_user_by_username(self, username: str) -> User | None:
        """Получение пользователя по никнейму."""
        statement = select(User).where(User.username == username)
        result = await self.db_session.execute(statement)
        return result.scalars().one_or_none()

    async def update_user_info(self, phone_number: str, update_data: dict) -> User:
        """Метод для обновления информации о пользователе."""
        statement = select(User).where(User.phone_number == phone_number)
        result = await self.db_session.execute(statement)
        user = result.scalars().one()

        if "username" in update_data:
            user.username = update_data["username"]
        if "height" in update_data:
            user.height = update_data["height"]

        if "steps" in update_data:
            new_steps = StepRecord(
                user_id=user.id,
                steps_count=update_data["steps"]["steps_count"],
                recorded_at=update_data["steps"]["recorded_at"]
            )
            self.db_session.add(new_steps)

        if "weight" in update_data:
            new_weight = WeightRecord(
                user_id=user.id,
                weight=update_data["weight"]["weight"],
                recorded_at=update_data["weight"]["recorded_at"]
            )
            self.db_session.add(new_weight)

        if "water" in update_data:
            new_water = WaterIntakeRecord(
                user_id=user.id,
                water_amount=update_data["water"]["water_amount"],
                recorded_at=update_data["water"]["recorded_at"]
            )
            self.db_session.add(new_water)

        await self.db_session.commit()
        await self.db_session.refresh(user)

        return user

    async def get_user_full_data(self, phone_number: str) -> User | None:
        """Метод для получения полной информации о пользователе, включая шаги, вес и воду."""
        statement = (
            select(User)
            .where(User.phone_number == phone_number, User.is_deleted == False)
            .options(
                selectinload(User.step_records),
                selectinload(User.weight_records),
                selectinload(User.water_intake_records)
            )
        )
        result = await self.db_session.execute(statement)
        return result.scalars().one_or_none()

    async def get_user_by_phone_number(self, phone_number: str) -> User | None:
        """Метод для получения пользователя по номеру телефона, если пользователя нет, то вернет None."""
        statement = select(User).where(User.phone_number == phone_number)
        result = await self.db_session.execute(statement)
        return result.scalars().one_or_none()

    async def create_user_by_phone_number(self, phone_number: str) -> User | None:
        """Создание пользователя в базе по номеру телефона."""
        statement = insert(User).values(
            id=uuid.uuid4(),
            phone_number=phone_number,
        ).returning(User)
        result = await self.db_session.execute(statement)
        new_record = result.scalars().one()
        await self.db_session.commit()

        return new_record

    async def create_phone_code_row(self, phone_number: str, last_4_digits: str) -> PhoneVerification:
        """Метод для создания строки с номером телефона и кода."""
        statement = insert(PhoneVerification).values(
            id=uuid.uuid4(),
            phone_number=phone_number,
            code=last_4_digits,
        ).returning(PhoneVerification)

        result = await self.db_session.execute(statement)
        new_record = result.scalars().one()
        await self.db_session.commit()

        return new_record

    async def check_code(self, phone_number: str, code: str) -> bool:
        """Метод для проверки правильности введенного кода и удаления записи."""

        statement = (select(PhoneVerification).where(PhoneVerification.phone_number == phone_number).where(
            PhoneVerification.code == code
        ))

        result = await self.db_session.execute(statement)
        verification_record = result.scalars().first()

        if verification_record is None:
            return False

        delete_statement = delete(PhoneVerification).where(PhoneVerification.id == verification_record.id)
        await self.db_session.execute(delete_statement)
        await self.db_session.commit()

        return True
