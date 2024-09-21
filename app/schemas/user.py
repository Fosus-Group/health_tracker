import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict
import phonenumbers


class TokenPayloadSchema(BaseModel):
    """Схема для хранения нагрузки токена"""
    exp: int = Field(
        ...,
        description="Время жизни токена.",
        example=[30],
    )
    sub: str = Field(
        ...,
        description="Строка идентификации токена.",
        examples=["+79180992344"],
    )


class UserStepsSchema(BaseModel):
    """Схема хранения шагов пользователя"""
    steps_count: int = Field(
        ...,
        description="Количество шагов",
        example=[9783]
    )
    recorded_at: datetime = Field(
        ...,
        description="Дата в которую были пройдены шаги",
        example=["2020-05-01T00:00:00Z"]
    )


class UserWeightSchema(BaseModel):
    """Схема хранения веса пользователя"""
    weight: float = Field(
        ...,
        description="Вес",
        example=[89.5]
    )
    recorded_at: datetime = Field(
        ...,
        description="Дата в которую был записан вес",
        example=["2020-05-01"]
    )


class UserWaterSchema(BaseModel):
    """Схема хранения выпитой воды пользователя"""
    water_amount: float = Field(
        ...,
        description="Вода.",
        example=[3.2]
    )
    recorded_at: datetime = Field(
        ...,
        description="Дата в которую было записано количество воды.",
        example=["2020-05-01"]
    )


class UserSchema(BaseModel):
    """Схема пользователя."""

    id: uuid.UUID = Field(
        ...,
        description="Идентификатор пользователя."
    )
    phone_number: str = Field(
        ...,
        description="Номер телефона.",
        examples=["+79182773844"],
    )
    username: str | None = Field(
        None,
        description="Никнейм пользователя.",
        examples=["user_1"],
    )
    avatar_hex: str | None = Field(
        None,
        description="Идентификатор аватара.",
        examples=["ff0ad7eceafa401295cde43ca33a6606"]
    )

    model_config = ConfigDict(from_attributes=True)


class UserDetailSchema(BaseModel):
    """Схема для показа полей пользователя."""

    phone_number: str = Field(
        ...,
        description="Номер телефона.",
        examples=["+79182773844"],
    )
    username: str | None = Field(
        None,
        description="Никнейм пользователя.",
        examples=["user_1"],
    )
    avatar_hex: str | None = Field(
        None,
        description="Идентификатор аватара.",
        examples=["ff0ad7eceafa401295cde43ca33a6606"]
    )
    height: int | None = Field(
        None,
        description="Рост пользователя.",
        examples=[180],
    )

    model_config = ConfigDict(from_attributes=True)


class TokenResponseSchema(BaseModel):
    """Схема для возврата на эндпоинте refresh."""
    access_token: str | None = Field(
        None,
        description="Access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzkajbsunjwldjnc"],
    )
    refresh_token: str | None = Field(
        None,
        description="Refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzkajbsunjwldjnc"],
    )


class UserUpdateSchema(BaseModel):
    """Схема для обновления данных пользователя."""
    username: str | None = Field(
        None,
        description="Никнейм пользователя.",
        examples=["user_1"],
    )
    height: int | None = Field(
        None,
        description="Рост пользователя.",
        examples=[180],
    )


class UserCallSchema(BaseModel):
    """Схема для отправки заявки на звонок по номеру."""

    phone_number: str = Field(
        ...,
        description="Номер телефона.",
        examples=["+79182773844"],
    )

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if v is None:
            return v
        try:
            phone_number = phonenumbers.parse(v, "RU")
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError("Invalid phone number")
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")
        return v


class BaseResponseSchema(BaseModel):
    """Схема возвращаемого значения при запросе на звонок."""

    success: bool = Field(
        ...,
        description="Статус запроса на звонок",
        examples=[True, False]
    )


class UserVerifyResponseSchema(BaseModel):
    """Схема возвращаемого значения при запросе на звонок."""

    success: bool = Field(
        ...,
        description="Статус запроса на звонок",
        examples=[True, False]
    )
    error: str | None = Field(
        None,
        description="Индикатор ошибки.",
        examples=["Invalid code"],
    )
    access_token: str | None = Field(
        None,
        description="Access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzkajbsunjwldjnc"],
    )
    refresh_token: str | None = Field(
        None,
        description="Refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzkajbsunjwldjnc"],
    )


class UserVerifySchema(BaseModel):
    """Схема для проверки правильно введенного кода."""
    phone_number: str = Field(
        ...,
        description="Номер телефона для проверки",
        examples=["+79182773844"],
    )
    code: str = Field(
        ...,
        description="Четырехзначный код, который ввел пользователь",
        examples=["0000"]
    )
