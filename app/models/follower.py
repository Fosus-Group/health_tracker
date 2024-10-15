from sqlalchemy import Column, ForeignKey, UUID, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class Follower(Base):
    """Модель подписок пользователей (followers)."""

    __tablename__ = "follower"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    # Пользователь, который подписан
    follower_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    # Пользователь, на которого подписан
    followed_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    follower = relationship("User", foreign_keys=[follower_id], backref="following")
    followed = relationship("User", foreign_keys=[followed_id], backref="followers")
