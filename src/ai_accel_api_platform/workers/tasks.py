from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from ai_accel_api_platform.ai.embeddings import embed_texts
from ai_accel_api_platform.db.repositories import upsert_item_with_embedding
from ai_accel_api_platform.db.session import get_redis, get_session
from ai_accel_api_platform.db.vector import bump_cache_namespace


def compute_and_store_embedding(
    item_id: str,
    content: str,
    metadata: dict[str, Any] | None,
) -> str:
    embedding = embed_texts([content])[0]

    async def _run() -> None:
        async with get_session() as session:
            await upsert_item_with_embedding(
                session,
                UUID(item_id),
                content,
                metadata,
                embedding,
            )
        try:
            redis = get_redis()
            await bump_cache_namespace(redis)
        except Exception:
            pass

    asyncio.run(_run())
    return item_id
