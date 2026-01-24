from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@postgres:5432/app", alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    jwt_secret: str = Field(default="change_me", alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")

    cors_origins_raw: str = Field(default="*", alias="CORS_ORIGINS")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    embedding_dim: int = Field(default=384, alias="EMBEDDING_DIM")
    prefer_gpu: bool = Field(default=True, alias="PREFER_GPU")
    embed_batch_size: int = Field(default=32, alias="EMBED_BATCH_SIZE")
    embed_quantize: bool = Field(default=False, alias="EMBED_QUANTIZE")
    embed_compile: bool = Field(default=False, alias="EMBED_COMPILE")

    enable_grpc: bool = Field(default=False, alias="ENABLE_GRPC")
    grpc_port: int = Field(default=50051, alias="GRPC_PORT")
    enable_rerank: bool = Field(default=False, alias="ENABLE_RERANK")
    rerank_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="RERANK_MODEL"
    )

    enable_tracing: bool = Field(default=False, alias="ENABLE_TRACING")

    cache_ttl_seconds: int = Field(default=30, alias="CACHE_TTL_SECONDS")

    rate_limit_requests: int = Field(default=60, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")

    default_admin_username: str = Field(default="admin", alias="DEFAULT_ADMIN_USERNAME")
    default_admin_password: str = Field(default="admin", alias="DEFAULT_ADMIN_PASSWORD")

    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")

    @property
    def cors_origins(self) -> List[str]:
        value = self.cors_origins_raw
        if value.strip() == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
