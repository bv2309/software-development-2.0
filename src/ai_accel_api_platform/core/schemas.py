from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str
    device: dict[str, Any]
    db_ok: bool


class ApiEndpointOrQueriedObjectInteractionType(str, Enum):
    GET_DATA = "GET_DATA"
    SEND_DATA = "SEND_DATA"


class ItemCreate(BaseModel):
    id: UUID | None = None
    content: str
    metadata: dict[str, Any] | None = None
    async_embedding: bool = False


class ItemRead(BaseModel):
    id: UUID
    content: str
    metadata: dict[str, Any] | None = None
    has_embedding: bool


class EmbeddingRequest(BaseModel):
    text: str | None = None
    texts: list[str] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> EmbeddingRequest:
        if not self.text and not self.texts:
            raise ValueError("text or texts must be provided")
        return self


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=100)
    filters: dict[str, Any] | None = None
    text_filter: str | None = None
    use_hybrid: bool = False


class SearchResult(BaseModel):
    id: UUID
    content: str
    metadata: dict[str, Any] | None
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: UUID
    username: str
    is_active: bool


class UserFullNameResponse(BaseModel):
    message: str
    full_name: str


class ErrorResponse(BaseModel):
    message: str
