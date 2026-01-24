from __future__ import annotations

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from ai_accel_api_platform.ai.embeddings import embed_texts
from ai_accel_api_platform.core.schemas import EmbeddingRequest, EmbeddingResponse

router = APIRouter()


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(payload: EmbeddingRequest) -> EmbeddingResponse:
    if payload.texts:
        texts = payload.texts
    else:
        texts = [payload.text or ""]
    embeddings = await run_in_threadpool(embed_texts, texts)
    return EmbeddingResponse(embeddings=embeddings)
