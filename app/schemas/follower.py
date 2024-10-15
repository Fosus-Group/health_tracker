from pydantic import BaseModel, Field
from uuid import UUID


class FollowActionSchema(BaseModel):
    """Схема для выполнения действия подписки/отписки."""

    user_id: UUID = Field(
        ...,
        description="ID пользователя, на которого нужно подписаться или отписаться."
    )
