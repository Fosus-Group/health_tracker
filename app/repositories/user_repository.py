from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete
from models.user import PhoneVerification
import uuid


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

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
