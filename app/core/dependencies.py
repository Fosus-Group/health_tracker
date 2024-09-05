from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import Settings, get_app_settings

app_settings: Settings = get_app_settings()

# PGSQL
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
