from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ai_accel_api_platform.ai.embeddings import embed_texts
from ai_accel_api_platform.ai.rerank import rerank_results
from ai_accel_api_platform.api.deps import get_db_session
from ai_accel_api_platform.core.schemas import SearchRequest, SearchResponse, SearchResult
from ai_accel_api_platform.db.repositories import hybrid_search, vector_search
from ai_accel_api_platform.db.session import get_redis
from ai_accel_api_platform.db.vector import build_search_cache_key, get_cache_namespace
from ai_accel_api_platform.settings import get_settings

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    payload: SearchRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SearchResponse:
    settings = get_settings()
    redis: Redis[str] | None = None
    cache_key = None
    try:
        redis = get_redis()
        namespace = await get_cache_namespace(redis)
        cache_key = build_search_cache_key(
            namespace,
            payload.query,
            payload.top_k,
            payload.filters,
            payload.text_filter,
        )

        cached = await redis.get(cache_key)
        if cached:
            data = SearchResponse.model_validate_json(cached)
            return data
    except Exception:
        redis = None

    embedding = await run_in_threadpool(embed_texts, [payload.query])

    if payload.use_hybrid or payload.text_filter:
        results = await hybrid_search(
            session,
            embedding[0],
            payload.top_k,
            payload.filters,
            payload.text_filter,
        )
    else:
        results = await vector_search(
            session,
            embedding[0],
            payload.top_k,
            payload.filters,
        )

    results = rerank_results(payload.query, results)

    response = SearchResponse(
        results=[
            SearchResult(
                id=item.id,
                content=item.content,
                metadata=item.metadata_,
                score=score,
            )
            for item, score in results
        ]
    )

    if redis is not None and cache_key is not None:
        await redis.set(cache_key, response.model_dump_json(), ex=settings.cache_ttl_seconds)
    return response
