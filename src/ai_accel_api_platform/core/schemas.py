from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str
    device: dict[str, Any]
    db_ok: bool


class ItemCreate(BaseModel):
    id: Optional[UUID] = None
    content: str
    metadata: Optional[dict[str, Any]] = None
    async_embedding: bool = False


class ItemRead(BaseModel):
    id: UUID
    content: str
    metadata: Optional[dict[str, Any]] = None
    has_embedding: bool


class EmbeddingRequest(BaseModel):
    text: Optional[str] = None
    texts: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_payload(self) -> "EmbeddingRequest":
        if not self.text and not self.texts:
            raise ValueError("text or texts must be provided")
        return self


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=100)
    filters: Optional[dict[str, Any]] = None
    text_filter: Optional[str] = None
    use_hybrid: bool = False


class SearchResult(BaseModel):
    id: UUID
    content: str
    metadata: Optional[dict[str, Any]]
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]


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
