from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, ConfigDict
import phonenumbers


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


class UserCallResponseSchema(BaseModel):
    """Схема возвращаемого значения при запросе на звонок."""

    success: bool = Field(
        ...,
        description="Статус запроса на звонок",
        examples=[True, False]
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
