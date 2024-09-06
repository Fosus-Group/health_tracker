from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from integrations.smsru.client import SmsRuClient


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.user_repository = UserRepository(db_session=db_session)
        self.smsru_client: SmsRuClient = SmsRuClient()

    async def phone_call(self, phone_number: str) -> bool:
        """Метод для запроса звонка на номер телефона."""
        async with SmsRuClient() as client:
            last_4_digits: str = await client.make_phone_call(phone_number=phone_number)

        await self.user_repository.create_phone_code_row(phone_number=phone_number, last_4_digits=last_4_digits)
        return True

    async def verify_code(self, phone_number: str, code: str) -> bool:
        """Метод для проверки правильно введенного кода."""
        return await self.user_repository.check_code(phone_number=phone_number, code=code)
