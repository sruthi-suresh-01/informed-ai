import json
from enum import Enum
from typing import Any, Literal, Self

from loguru import logger as log
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

APP_ENV = os.getenv("APP_ENV", "DEV")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER_NAME = os.getenv("DB_SERVER_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE_NAME = os.getenv("DB_DATABASE_NAME")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:toor@localhost:5432/Informed")

GPT_APIKEY = os.getenv("GPT_APIKEY", "")
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME", "gpt-3.5-turbo")

ENV_VARS = {
    "DB_USERNAME": DB_USERNAME,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_SERVER_NAME": DB_SERVER_NAME,
    "DB_PORT": DB_PORT,
    "DB_DATABASE_NAME": DB_DATABASE_NAME,
    "DB_URL": DB_URL,
    "APP_ENV": APP_ENV,
    "GPT_APIKEY": GPT_APIKEY,
    "GPT_MODEL_NAME": GPT_MODEL_NAME,
}


class SafeDumpableModel(BaseModel):
    # pydantic fields defined with Field(exclude=True) will be omitted from model_dump
    # however exclude=False is the default so we risk leaking sensitive data if we forget to set it explicitly
    # instead we use this method to redact any data that does not explicitly set exclude=False
    def safe_model_dump(self) -> dict[str, Any]:
        dump = super().model_dump(exclude_unset=True)
        for name, field in self.model_fields.items():
            value = getattr(self, name)
            if isinstance(value, SafeDumpableModel):
                dump[name] = value.safe_model_dump()
            elif field.exclude is not False:
                dump[name] = "[REDACTED]"

        return dump


class OpenTelemetryTracingConfig(SafeDumpableModel):
    enabled: bool = Field(default=False, exclude=False)
    sample_rate: float = Field(default=1.0, exclude=False)


class TelemetryConfig(SafeDumpableModel):
    enabled: bool = Field(default=False, exclude=False)
    console_enabled: bool = Field(default=False, exclude=False)
    opentelemetry_config: OpenTelemetryTracingConfig = OpenTelemetryTracingConfig(
        enabled=True
    )


class UIConfig(SafeDumpableModel):
    web_url: str = Field(default="http://localhost:3000/", exclude=False)


class AuthConfig(SafeDumpableModel):
    auth_mode: Literal["SUPERUSER", "FULL"] = Field(default="FULL", exclude=False)


class LoggingConfig(SafeDumpableModel):
    level: str = "DEBUG"
    enable_console: bool = False
    jsonify: bool = False


class ConnectionPoolConfig(SafeDumpableModel):
    max_pool_size: int = Field(default=10, exclude=False)
    max_overflow: int = Field(default=20, exclude=False)


class DatabaseConfig(SafeDumpableModel):
    db_url: str = Field(default="", exclude=True)
    connection_pool_config: ConnectionPoolConfig = ConnectionPoolConfig()

    @model_validator(mode="after")
    def verify_db_url_is_set(self) -> Self:
        if not self.db_url:
            raise ValueError("db_url is required for database config")
        return self


class Config(SafeDumpableModel, BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.overrides"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    service_name: str = "informed-core"
    database_config: DatabaseConfig
    telemetry_config: TelemetryConfig = TelemetryConfig()

    ui_config: UIConfig = UIConfig()
    cache_timestamps: bool = Field(default=False, exclude=False)
    logging_config: LoggingConfig = LoggingConfig()
    auth_config: AuthConfig

    @classmethod
    def from_env(cls) -> "Config":
        return cls.model_validate({})


def get_config(print_config: bool = False) -> Config:
    config = Config.from_env()
    if print_config:
        log.info(json.dumps(config.safe_model_dump()))
    return config
