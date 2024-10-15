from uuid import UUID
from models.follower import Follower
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class FollowerRepository:
    """Репозиторий для работы с подписками пользователей."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def check_follower(self, follower_id: UUID, followed_id: UUID) -> Follower:
        """Метод для проверки наличия существующей подписки."""
        statement = select(Follower).where(
            Follower.follower_id == follower_id,
            Follower.followed_id == followed_id
        )
        result = await self.db_session.execute(statement)
        existing_follow = result.scalars().first()
        return existing_follow

    async def add_follow(self, follower_id: UUID, followed_id: UUID) -> None:
        """Метод для добавления подписки."""
        new_follow = Follower(follower_id=follower_id, followed_id=followed_id)
        self.db_session.add(new_follow)
        await self.db_session.commit()

    async def remove_follow(self, follower_id: UUID, followed_id: UUID) -> None:
        """Метод для удаления подписки."""
        existing_follow = await self.check_follower(follower_id, followed_id)
        await self.db_session.delete(existing_follow)
        await self.db_session.commit()
