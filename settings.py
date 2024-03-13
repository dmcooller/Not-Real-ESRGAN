import logging
import os
import secrets
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _get_env_file() -> Path:
    try:
        env = os.environ["APP_ENV"]
    except KeyError:
        env = "development"
    logger.warning("Loading `%s` environment", env)
    return Path(__file__).parent / f"config/{env}.env"


class Settings(BaseSettings):
    PROJECT_NAME: str
    APP_NAME: str | None = None
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = False
    ALLOW_ORIGINS: list = ["*"]

    LOG_LEVEL: str = "INFO"
    LOG_DESTINATIONS: list = ["console"]

    UVICORN_ACCESS_LOG_LEVEL: str = "INFO"
    UVICORN_ERROR_LOG_LEVEL: str = "INFO"
    UVICORN_LOG_HANDLERS: list = ["console"]

    SENTRY_DSN: str | None = None

    API_V1_STR: str = "/api/v1"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=_get_env_file(),
    )

settings = Settings()
