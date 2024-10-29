import json
from enum import Enum
from typing import Any, Literal, Self

from loguru import logger as log
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class WeatherSource(str, Enum):
    WEATHERAPI = "weatherapi"


class WeatherSourceConfig(BaseModel):
    source: WeatherSource
    api_key: str | None = None


class WeatherAPIConfig(WeatherSourceConfig):
    source: WeatherSource = WeatherSource.WEATHERAPI


class WeatherSourcesConfig(BaseModel):
    weatherapi: WeatherAPIConfig | None = None


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


class RedisConfig(SafeDumpableModel):
    host: str = Field(default="localhost", exclude=False)
    port: int = Field(default=6379, exclude=False)
    db: int = Field(default=0, exclude=False)
    decode_responses: bool = Field(default=True, exclude=False)


class LLMProvider(str, Enum):
    OPENAI = "openai"


class OpenAiConfig(BaseModel):
    api_key: str


class LLMConfig(BaseModel):
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_model: str = "gpt-4o-mini-2024-07-18"
    temperature: float = 0.0
    max_tokens: int = 150
    openai_config: OpenAiConfig | None = None


class Config(SafeDumpableModel, BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.overrides"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    llm_config: LLMConfig = LLMConfig()

    service_name: str = "informed-core"
    database_config: DatabaseConfig
    redis_config: RedisConfig = RedisConfig()
    telemetry_config: TelemetryConfig = TelemetryConfig()

    weather_sources_config: WeatherSourcesConfig = WeatherSourcesConfig()

    ui_config: UIConfig = UIConfig()
    cache_timestamps: bool = Field(default=False, exclude=False)
    logging_config: LoggingConfig = LoggingConfig()

    @classmethod
    def from_env(cls) -> "Config":
        return cls.model_validate({})


def get_config(print_config: bool = False) -> Config:
    config = Config.from_env()
    if print_config:
        log.info(json.dumps(config.safe_model_dump()))
    return config
