from typing import Annotated

from core.dependencies import get_user_service
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.user import UserCallSchema, UserCallResponseSchema, UserVerifySchema, UserVerifyResponseSchema
from schemas.problem import ProblemDetail

from services.user_service import UserService

router = APIRouter(prefix="/user", tags=["Пользователи."])


@router.post(
    "/call",
    status_code=status.HTTP_200_OK,
    response_model=UserCallResponseSchema,
    summary="Запрос на авторизацию по номеру телефона.",
    responses={
        200: {
            "model": UserCallResponseSchema,
            "description": "Запрос успешно отправлен.",
        },
        422: {
            "model": ProblemDetail,
            "description": "Неправильно набран номер.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def make_phone_call(
    user_service: Annotated[UserService, Depends(get_user_service)],
    phone_to_call: UserCallSchema,
) -> UserCallResponseSchema:
    """Эндпоинт для запроса на отправку на номер телефона."""
    result: bool = await user_service.phone_call(phone_number=phone_to_call.phone_number)
    return UserCallResponseSchema(success=result)


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=UserVerifyResponseSchema,
    summary="Проверка кода подтверждения.",
    responses={
        200: {
            "model": UserVerifyResponseSchema,
            "description": "Код успешно проверен.",
        },
        400: {
            "model": ProblemDetail,
            "description": "Код неверен или истек.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def verify_phone_call(
    user_service: Annotated[UserService, Depends(get_user_service)],
    verification_data: UserVerifySchema,
) -> UserVerifyResponseSchema:
    """Эндпоинт для проверки кода подтверждения."""
    check_code: UserVerifyResponseSchema = await user_service.verify_code(
        phone_number=verification_data.phone_number,
        code=verification_data.code
    )

    if check_code.error == "Invalid code":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный код.")

    return check_code
