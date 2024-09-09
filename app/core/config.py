import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    environment: str = "production"

    debug: bool = False

    docs_url: str = "/api/docs"
    openapi_url: str = "/api/openapi.json"
    redoc_url: str = "/api/redoc"
    api_prefix: str = "/api"

    title: str = "Health tracker"
    version: str = "0.1.0"
    summary: str = ""
    description: str = "Приложение для отслеживания здоровья"

    pg_host: str = "localhost"
    pg_port: str = "5432"
    pg_database: str = "health_tracker"
    pg_username: str = "postgres"
    pg_password: str = "example"
    pool_size: int = 20

    enable_cors: bool = True
    cors_origins: list[str] = ["*"]

    allowed_hosts: list[str] | None = ["localhost"]
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"))


@lru_cache
def get_app_settings() -> Settings:
    """Retrieve the application settings.

    Returns
    -------
        Settings: The application settings.

    """
    return Settings()


def get_settings_no_cache() -> Settings:
    """Получение настроек без кеша."""
    return Settings()
