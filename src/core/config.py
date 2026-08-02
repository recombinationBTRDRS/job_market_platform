# src/core/config.py
from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Job Market Analytics Platform")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    secret_key: str = Field(min_length=32)
    allowed_hosts: list[str] = Field(default=["localhost", "127.0.0.1"])

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    database_url: PostgresDsn

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_url: RedisDsn

    # JWT
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # ETL
    etl_schedule_interval: str = Field(default="0 */6 * * *")
    etl_max_retries: int = Field(default=3)
    etl_batch_size: int = Field(default=100)


@lru_cache
def get_settings() -> Settings:
    return Settings()
