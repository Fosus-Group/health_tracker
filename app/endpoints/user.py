from typing import Annotated

from core.dependencies import get_user_service, get_current_user, oauth_scheme
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.user import (
    UserCallSchema,
    UserCallResponseSchema,
    UserVerifySchema,
    UserVerifyResponseSchema,
    UserSchema,
    UserDetailSchema,
    UserUpdateSchema,
    TokenResponseSchema,
)
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
    user_verify: UserVerifyResponseSchema = await user_service.verify_code(
        phone_number=verification_data.phone_number,
        code=verification_data.code
    )

    if user_verify.error == "Invalid code":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный код.")

    return user_verify


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponseSchema,
    summary="Обновление access токена по refresh токену.",
    responses={
        200: {
            "model": TokenResponseSchema,
            "description": "Новый access токен успешно создан.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Refresh токен недействителен или истек.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def refresh_access_token(
    user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    token: str = Depends(oauth_scheme),
) -> TokenResponseSchema:
    """Эндпоинт для обновления access токена с использованием refresh токена."""
    access_token = await user_service.create_jwt_token(subject=user.phone_number, is_refresh=False)

    return TokenResponseSchema(
        access_token=access_token,
        refresh_token=token
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserDetailSchema,
    summary="Получение информации о пользователе.",
    responses={
        200: {
            "model": UserDetailSchema,
            "description": "Информация успешно получена.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def get_user_details(
    user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    return await user_service.get_full_info_about_user(phone_number=user.phone_number)


@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=UserDetailSchema,
    summary="Обновление полей пользователя.",
    responses={
        200: {
            "model": UserDetailSchema,
            "description": "Поля успешно обновлены.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def update_user_info(
    user_update_data: UserUpdateSchema,
    user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    if user_update_data.username:
        is_exists: bool = await user_service.check_if_username_exists(username=user_update_data.username)
        if is_exists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Пользователь с таким username уже существует.",
            )
    return await user_service.update_user_info(phone_number=user.phone_number, data=user_update_data)
