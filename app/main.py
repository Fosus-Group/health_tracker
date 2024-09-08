import logging
from pathlib import Path

from core.config import Settings, get_app_settings
from core.exception_handler import (
    all_exception_handler,
    custom_validation_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler,
)
from core.logging_config import setup_json_logging
from endpoints.api import routers
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


def get_application() -> FastAPI:
    """Returns the FastAPI application instance."""
    settings: Settings = get_app_settings()

    if settings.environment != "development":
        setup_json_logging()
        logger = logging.getLogger("health_tracker")
        logger.warning("Running in production mode")

    application = FastAPI(
        **settings.model_dump(),
        separate_input_output_schemas=False,
    )

    if settings.allowed_hosts:
        from fastapi.middleware.cors import CORSMiddleware

        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(routers, prefix=settings.api_prefix)

    static_dir = Path("static")
    if static_dir.is_dir():
        application.mount("/health_tracker/static", StaticFiles(directory="static"), name="static")

    application.add_exception_handler(RequestValidationError, custom_validation_exception_handler)  # type: ignore
    application.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    application.add_exception_handler(Exception, all_exception_handler)  # type: ignore
    application.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)  # type: ignore

    return application


app = get_application()
