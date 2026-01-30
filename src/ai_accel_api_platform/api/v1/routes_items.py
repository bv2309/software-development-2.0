from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from rq import Queue
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ai_accel_api_platform.ai.embeddings import embed_texts
from ai_accel_api_platform.api.deps import get_db_session
from ai_accel_api_platform.core.schemas import ItemCreate, ItemRead
from ai_accel_api_platform.db.repositories import get_item, upsert_item_with_embedding
from ai_accel_api_platform.db.session import get_redis, get_sync_redis
from ai_accel_api_platform.db.vector import bump_cache_namespace
from ai_accel_api_platform.workers.tasks import compute_and_store_embedding

router = APIRouter()


@router.post("/items", response_model=ItemRead)
async def upsert_item(
    payload: ItemCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRead:
    item_id = payload.id or uuid4()

    if payload.async_embedding:
        item = await upsert_item_with_embedding(
            session,
            item_id,
            payload.content,
            payload.metadata,
            None,
        )
        redis_conn = get_sync_redis()
        queue = Queue(connection=redis_conn)
        queue.enqueue(
            compute_and_store_embedding,
            str(item_id),
            payload.content,
            payload.metadata,
        )
    else:
        embedding = await run_in_threadpool(embed_texts, [payload.content])
        item = await upsert_item_with_embedding(
            session,
            item_id,
            payload.content,
            payload.metadata,
            embedding[0],
        )

    try:
        redis = get_redis()
        await bump_cache_namespace(redis)
    except Exception:
        pass

    return ItemRead(
        id=item.id,
        content=item.content,
        metadata=item.metadata_,
        has_embedding=item.embedding is not None,
    )


@router.get("/items/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRead:
    item = await get_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemRead(
        id=item.id,
        content=item.content,
        metadata=item.metadata_,
        has_embedding=item.embedding is not None,
    )
