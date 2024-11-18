from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import Settings, get_app_settings
from repositories.follower_repository import FollowerRepository

app_settings: Settings = get_app_settings()


class FollowerService:
    """Сервис для работы с подписками пользователей."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.follow_repository = FollowerRepository(db_session=db_session)

    async def follow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        """Метод для подписки на пользователя."""
        await self.follow_repository.add_follow(follower_id, followed_id)

    async def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        """Метод для отписки от пользователя."""
        await self.follow_repository.remove_follow(follower_id, followed_id)

    async def check_follower(self, follower_id: UUID, followed_id: UUID) -> bool:
        """Метод для проверки подписки пользователя."""
        return await self.follow_repository.check_follower(follower_id, followed_id)
