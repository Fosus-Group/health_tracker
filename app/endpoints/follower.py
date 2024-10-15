from fastapi import APIRouter, status, Depends, HTTPException
from schemas.user import BaseResponseSchema
from schemas.problem import ProblemDetail
from core.dependencies import get_current_user, get_follow_service
from services.follower_service import FollowerService
from schemas.user import UserSchema
from schemas.follower import FollowActionSchema

router = APIRouter(prefix="/follower", tags=["Подписчики."])


@router.post(
    "/follow",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
    summary="Подписка на пользователя.",
    responses={
        200: {
            "model": BaseResponseSchema,
            "description": "Пользователь успешно подписан.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        404: {
            "description": "Пользователь не найден.",
            "model": ProblemDetail,
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def follow_user(
    follow_data: FollowActionSchema,
    user: UserSchema = Depends(get_current_user),
    follow_service: FollowerService = Depends(get_follow_service),
) -> BaseResponseSchema:
    """Эндпоинт для подписки на пользователя."""
    if user.id == follow_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя подписаться на самого себя."
        )

    existing_follow = await follow_service.check_follower(user.id, follow_data.user_id)
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже подписаны на этого пользователя."
        )

    await follow_service.follow_user(follower_id=user.id, followed_id=follow_data.user_id)
    return BaseResponseSchema(success=True)


@router.delete(
    "/unfollow",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
    summary="Отписка от пользователя.",
    responses={
        200: {
            "model": BaseResponseSchema,
            "description": "Пользователь успешно отписан.",
        },
        401: {
            "model": ProblemDetail,
            "description": "Пользователь не авторизован.",
        },
        404: {
            "description": "Пользователь не найден.",
            "model": ProblemDetail,
        },
        500: {"description": "Внутренняя ошибка сервера.", "model": ProblemDetail},
    },
)
async def unfollow_user(
    follow_data: FollowActionSchema,
    user: UserSchema = Depends(get_current_user),
    follow_service: FollowerService = Depends(get_follow_service),
) -> BaseResponseSchema:
    """Эндпоинт для отписки от пользователя."""
    if user.id == follow_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отписаться от самого себя."
        )

    existing_follow = await follow_service.check_follower(user.id, follow_data.user_id)
    if not existing_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не подписаны на этого пользователя."
        )

    await follow_service.unfollow_user(follower_id=user.id, followed_id=follow_data.user_id)
    return BaseResponseSchema(success=True)
