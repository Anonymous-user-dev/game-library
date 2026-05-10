from __future__ import annotations

from pathlib import Path

import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    APP_ENV: str = "development"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "localhost"
    ALLOWED_ORIGINS: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

logger.info(f"DB IN USE: {settings.DATABASE_URL}")