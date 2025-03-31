"""
Application settings module.
"""

from functools import lru_cache
from typing import Optional, Union

from pydantic import AnyUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings


class SQLiteURL(AnyUrl):
    allowed_schemes = {"sqlite"}
    host_required = False


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dotmac Platform Core"
    VERSION: str = "0.1.0"

    # Environment
    ENV: str = "development"
    DEBUG: bool = ENV == "development"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # Database
    DATABASE_URL: Optional[Union[PostgresDsn, SQLiteURL]] = None
    TEST_DATABASE_URL: str = "sqlite:///:memory:"

    # Redis
    REDIS_URL: Optional[RedisDsn] = None

    # Security
    SECRET_KEY: str = "dev_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        """
        Parse CORS origins from string or list.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()
