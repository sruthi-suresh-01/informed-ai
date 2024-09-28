import json
from enum import Enum
from typing import Any, Literal, Self

from loguru import logger as log
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class CacheKind(str, Enum):
    FILE = "file"
    INMEMORY = "inmemory"
    DATABASE = "db"


class CacheConfig(SafeDumpableModel):
    enabled: bool = Field(default=False, exclude=False)
    kind: CacheKind = Field(default=CacheKind.FILE, exclude=False)
    name: str = Field(exclude=False)
    store: dict[str, Any] = {}


class RetrievalConfig(SafeDumpableModel):
    enabled: bool = Field(default=True, exclude=False)
    kubernetes_max_results: int = Field(default=10, exclude=False)
    confluence_max_results: int = Field(default=25, exclude=False)
    # GPT-4o has a context window of 128k tokens, Sonnet has 200k tokens.
    # Divide the confluence_source_text_max_chars by 4 and
    # multiply by confluence_max_results to get the estimated token count
    confluence_source_text_max_chars: int = Field(default=6000, exclude=False)
    similarity_threshold: float = Field(default=0.0, exclude=False)
    max_retrieval_attempts: int = Field(default=3, exclude=False)


class AzureOpenAILLMConfig(SafeDumpableModel):
    api_key: SecretStr
    api_version: str = Field(default="2024-05-01-preview", exclude=False)
    api_base: str = Field(
        default="https://azure-oai-1.openai.azure.com/", exclude=False
    )


class OpenAILLMConfig(SafeDumpableModel):
    api_key: SecretStr


class AnthropicLLMConfig(SafeDumpableModel):
    api_key: SecretStr


class VertexAILLMConfig(SafeDumpableModel):
    vertex_ai_project: str
    vertex_ai_location: str = Field(exclude=False)


class VertexAIEmbeddingConfig(SafeDumpableModel):
    vertex_ai_project: str
    vertex_ai_location: str = Field(exclude=False)

    # High RPM regions have RPM of 1500 for default `textembedding-gecko@003` embedding model
    # Low RPM regions have RPM of 100 for `textembedding-gecko@003` embedding model
    # See quotas for more info: https://cloud.google.com/vertex-ai/generative-ai/docs/quotas
    @property
    def has_high_rpm(self) -> bool:
        return self.vertex_ai_location == "us-central1"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
    VERTEX_AI = "vertex_ai"  # this works for sonnet but not gemini
    VERTEX_AI_BETA = "vertex_ai_beta"  # this works for gemini but not sonnet


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    AZURE = "azure"
    VERTEX_AI = "vertex_ai"


# See instructions in READMD.md for switching between different LLM/embedding providers or models
class LLMConfig(SafeDumpableModel):
    # TODO (peter): support different models at the request level
    cache_config: CacheConfig = CacheConfig(
        enabled=False, kind=CacheKind.INMEMORY, name="llm_cache"
    )
    llm_provider: LLMProvider = Field(exclude=False)
    llm_model_name: str = Field(exclude=False)
    embedding_provider: EmbeddingProvider = Field(exclude=False)
    embedding_model_name: str = Field(exclude=False)
    embedding_max_tokens: int = Field(exclude=False)
    embedding_max_concurrency: int = Field(exclude=False)
    embedding_batch_size: int = Field(exclude=False)
    azure: AzureOpenAILLMConfig | None = None
    openai: OpenAILLMConfig | None = None
    anthropic: AnthropicLLMConfig | None = None
    # we separate the vertex config because we often want to use different regions for LLMs and embedding models
    vertex_llm: VertexAILLMConfig | None = None
    vertex_embedding: VertexAIEmbeddingConfig | None = None
    temperature: float = Field(default=0.0, exclude=False)
    wait_on_retry: bool = Field(default=True, exclude=False)

    def validate_api_keys_are_set(self) -> None:
        if (
            self.llm_provider == LLMProvider.OPENAI
            or self.embedding_provider == EmbeddingProvider.OPENAI
        ) and (not self.openai):
            raise ValueError("OpenAI API key is not set")

        if (
            self.llm_provider == LLMProvider.AZURE
            or self.embedding_provider == EmbeddingProvider.AZURE
        ) and (not self.azure):
            raise ValueError("Azure OpenAI API key is not set")

        if self.llm_provider == LLMProvider.ANTHROPIC and not self.anthropic:
            raise ValueError("Anthropic API key is not set")

    @property
    def llm_model(self) -> str:
        return self.llm_provider + "/" + self.llm_model_name

    @property
    def llm_params(self) -> dict[str, Any]:
        params: BaseModel | None = None
        if self.llm_provider == LLMProvider.OPENAI and self.openai:
            params = self.openai
        if self.llm_provider == LLMProvider.AZURE and self.azure:
            params = self.azure
        if self.llm_provider == LLMProvider.ANTHROPIC and self.anthropic:
            params = self.anthropic
        if (
            self.llm_provider in [LLMProvider.VERTEX_AI, LLMProvider.VERTEX_AI_BETA]
            and self.vertex_llm
        ):
            params = self.vertex_llm
        if params is not None:
            params_dict = params.model_dump()
            for name, annotation in params.__annotations__.items():
                if annotation == SecretStr and name in params_dict:
                    params_dict[name] = getattr(params, name).get_secret_value()
            return params_dict
        raise ValueError(f"invalid parameters for LLM provider: {self.llm_provider}")

    @property
    def embedding_model(self) -> str:
        return self.embedding_provider + "/" + self.embedding_model_name

    @property
    def embedding_params(self) -> dict[str, Any]:
        params: BaseModel | None = None
        if self.embedding_provider == EmbeddingProvider.OPENAI and self.openai:
            params = self.openai
        if self.embedding_provider == EmbeddingProvider.AZURE and self.azure:
            params = self.azure
        if (
            self.embedding_provider == EmbeddingProvider.VERTEX_AI
            and self.vertex_embedding
        ):
            params = self.vertex_embedding
        if params is not None:
            params_dict = params.model_dump()
            for name, annotation in params.__annotations__.items():
                if annotation == SecretStr and name in params_dict:
                    params_dict[name] = getattr(params, name).get_secret_value()
            return params_dict
        raise ValueError(
            f"invalid parameters for embedding provider: {self.embedding_provider}"
        )


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
