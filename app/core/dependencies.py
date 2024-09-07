from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import Settings, get_app_settings
from repositories.user_repository import UserRepository
from services.user_service import UserService
from schemas.user import UserSchema, TokenPayload
from models.user import User
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt
from datetime import datetime
from pydantic import ValidationError

app_settings: Settings = get_app_settings()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


pg_connection_string = (
    f"postgresql+asyncpg://{app_settings.pg_username}:{app_settings.pg_password}@"
    f"{app_settings.pg_host}:{app_settings.pg_port}/{app_settings.pg_database}"
)

async_engine = create_async_engine(
    pg_connection_string,
    pool_pre_ping=True,
    pool_size=app_settings.pool_size,
)

async_session = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession, autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии с базой данных."""
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    """Возвращает экземпляр UserService."""
    return UserService(db_session=db)


async def get_current_user(
    token: str = Depends(oauth_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    try:
        payload = jwt.decode(
            token, app_settings.jwt_secret_key, algorithms=[app_settings.jwt_algorithm]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: UserSchema = await user_service.get_user_by_phone_number(phone_number=token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user
