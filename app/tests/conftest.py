import pytest
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from models import Base
from core.config import get_app_settings
from models.user import User
from tests.data.user import test_users_data
from fastapi import FastAPI
from main import get_application
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport


get_app_settings.cache_clear()
settings = get_app_settings()

os.environ["PG_HOST"] = "localhost"
os.environ["PG_PORT"] = "5432"
os.environ["PG_USER"] = "postgres"
os.environ["PG_PASSWORD"] = "example"
os.environ["PG_DATABASE"] = "health_tracker"
os.environ["DEBUG"] = "True"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "app/tests", "docker-compose.yml")


def is_postgres_responsive():
    pg_connection_string = (
        f"postgresql+psycopg2://{settings.pg_username}:{settings.pg_password}@"
        f"{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"
    )
    print(f"pg_connection_string: {pg_connection_string}")
    try:
        engine = create_engine(pg_connection_string, echo=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def check_postgres_responsive(docker_services):
    docker_services.wait_until_responsive(
        timeout=30.0, pause=1.0, check=is_postgres_responsive
    )


@pytest.fixture(scope="session")
def postgresql(docker_services):
    """Запускает postgres перед тестами и останавливает после"""


@pytest.fixture(scope="session")
async def fill_test_data(postgresql):
    pg_connection_string = (
        f"postgresql+asyncpg://{settings.pg_username}:{settings.pg_password}@"
        f"{settings.pg_host}:{settings.pg_port}/{settings.pg_database}"
    )
    engine = create_async_engine(pg_connection_string, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            shops = [
                User(
                    id=data["id"],
                    phone_number=data["phone_number"]
                )
                for data in test_users_data
            ]
            session.add_all(shops)
        await session.commit()

    yield

    async with async_session() as session:
        async with session.begin():
            await session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE'))
        await session.commit()

    await engine.dispose()


@pytest.fixture(scope="session")
def app(postgresql, check_postgres_responsive, fill_test_data) -> FastAPI:
    return get_application()


@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client
