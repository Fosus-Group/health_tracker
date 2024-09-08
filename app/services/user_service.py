from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from integrations.smsru.client import SmsRuClient
from datetime import timedelta
from datetime import datetime, timezone
from core.config import Settings, get_app_settings
from jose import jwt
from schemas.user import (
    UserSchema,
    UserVerifyResponseSchema,
    UserDetailSchema,
    UserStepsSchema,
    UserWeightSchema,
    UserWaterSchema,
    UserUpdateSchema,
)

app_settings: Settings = get_app_settings()


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.user_repository = UserRepository(db_session=db_session)
        self.smsru_client: SmsRuClient = SmsRuClient()

    async def check_if_username_exists(self, username: str) -> bool:
        """Метод для проверки существует ли пользователь в базе с таким никнеймом."""
        user = await self.user_repository.get_user_by_username(username=username)
        return user is not None

    async def update_user_info(self, phone_number: str, data: UserUpdateSchema) -> UserDetailSchema:
        """Метод для обновления полей пользователя."""
        update_data = data.dict(exclude_unset=True)
        updated_user = await self.user_repository.update_user_info(phone_number, update_data)

        steps = [
            UserStepsSchema(steps_count=step.steps_count, recorded_at=step.recorded_at)
            for step in updated_user.step_records]
        weight = [
            UserWeightSchema(weight=weight_record.weight, recorded_at=weight_record.recorded_at)
            for weight_record in updated_user.weight_records]
        water = [
            UserWaterSchema(water_amount=water_record.water_amount, recorded_at=water_record.recorded_at)
            for water_record in updated_user.water_intake_records
        ]

        return UserDetailSchema(
            phone_number=updated_user.phone_number,
            username=updated_user.username,
            height=updated_user.height,
            steps=steps,
            weight=weight,
            water=water
        )

    async def get_full_info_about_user(self, phone_number: str) -> UserDetailSchema:
        """Метод для получения полной информации о пользователе."""
        user_data = await self.user_repository.get_user_full_data(phone_number=phone_number)

        steps = [UserStepsSchema(steps_count=step.steps_count, recorded_at=step.recorded_at) for step in
                 user_data.step_records]
        weight = [UserWeightSchema(weight=weight_record.weight, recorded_at=weight_record.recorded_at) for weight_record
                  in user_data.weight_records]
        water = [UserWaterSchema(water_amount=water_record.water_amount, recorded_at=water_record.recorded_at) for
                 water_record in user_data.water_intake_records]

        return UserDetailSchema(
            phone_number=user_data.phone_number,
            username=user_data.username,
            height=user_data.height,
            steps=steps,
            weight=weight,
            water=water
        )

    async def get_user_by_phone_number(self, phone_number: str) -> UserSchema | None:
        """Метод для получения пользователя по номеру телефона."""
        user = await self.user_repository.get_user_by_phone_number(phone_number=phone_number)
        return UserSchema.from_orm(user) if user else None

    async def create_user_by_phone_number(self, phone_number: str) -> UserSchema:
        """Метод для создания пользователя по номеру телефона."""
        user = await self.user_repository.create_user_by_phone_number(phone_number=phone_number)
        return UserSchema.from_orm(user)

    async def phone_call(self, phone_number: str) -> bool:
        """Метод для запроса звонка на номер телефона."""
        async with SmsRuClient() as client:
            last_4_digits: str = await client.make_phone_call(phone_number=phone_number)

        await self.user_repository.create_phone_code_row(phone_number=phone_number, last_4_digits=last_4_digits)
        return True

    async def verify_code(self, phone_number: str, code: str) -> UserVerifyResponseSchema:
        """Метод для проверки правильно введенного кода."""
        is_valid = await self.user_repository.check_code(phone_number=phone_number, code=code)
        if not is_valid:
            return UserVerifyResponseSchema(
                success=False,
                error="Invalid code",
            )

        user: UserSchema | None = await self.get_user_by_phone_number(phone_number=phone_number)
        if user:
            access_token = await self.create_jwt_token(subject=phone_number, is_refresh=False)
            refresh_token = await self.create_jwt_token(subject=phone_number, is_refresh=True)
            return UserVerifyResponseSchema(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        await self.create_user_by_phone_number(phone_number=phone_number)
        access_token = await self.create_jwt_token(subject=phone_number, is_refresh=False)
        refresh_token = await self.create_jwt_token(subject=phone_number, is_refresh=True)
        return UserVerifyResponseSchema(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def create_jwt_token(self, subject: str, is_refresh: bool, expires_delta: timedelta = None) -> str:
        """Метод для генерирования токена."""
        expire_minutes = app_settings.refresh_token_expire_minutes if is_refresh else app_settings.access_token_expire_minutes
        jwt_key = app_settings.jwt_refresh_secret_key if is_refresh else app_settings.jwt_secret_key

        if expires_delta:
            expires_delta = datetime.now(timezone.utc) + expires_delta
        else:
            expires_delta = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

        to_encode = {"exp": expires_delta, "sub": subject}
        encoded_jwt = jwt.encode(to_encode, jwt_key, app_settings.jwt_algorithm)
        return encoded_jwt
