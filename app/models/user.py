import uuid

from core.config import Settings, get_app_settings
from sqlalchemy import Boolean, Column, DateTime, String, func, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime
from datetime import timedelta

from models.base import Base

app_settings: Settings = get_app_settings()


class WeightRecord(Base):
    """Модель для хранения записей о весе пользователя."""

    __tablename__ = "weight_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    weight = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="weight_records")


class WaterIntakeRecord(Base):
    """Модель для хранения записей о выпитой воде пользователя."""

    __tablename__ = "water_intake_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    water_amount = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="water_intake_records")


class StepRecord(Base):
    """Модель для хранения записей о количестве пройденных шагов пользователя."""

    __tablename__ = "step_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    steps_count = Column(Integer, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="step_records")


class PhoneVerification(Base):
    """Модель для хранения кодов подтверждения."""

    __tablename__ = "phone_verification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    code = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    username = Column(String, nullable=True)
    height = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, index=True, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    weight_records = relationship("WeightRecord", back_populates="user", cascade="all, delete-orphan")
    water_intake_records = relationship("WaterIntakeRecord", back_populates="user", cascade="all, delete-orphan")
    step_records = relationship("StepRecord", back_populates="user", cascade="all, delete-orphan")
