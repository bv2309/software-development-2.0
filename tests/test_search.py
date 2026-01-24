from __future__ import annotations

import os
from uuid import uuid4

import pytest

from ai_accel_api_platform.db.repositories import upsert_item_with_embedding, vector_search
from ai_accel_api_platform.db.session import get_session
from ai_accel_api_platform.db.vector import build_search_cache_key
from ai_accel_api_platform.settings import get_settings


def test_cache_key_deterministic():
    key1 = build_search_cache_key("1", "Hello", 5, {"b": 2, "a": 1}, None)
    key2 = build_search_cache_key("1", "hello", 5, {"a": 1, "b": 2}, None)
    assert key1 == key2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_vector_search_integration():
    if not os.getenv("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set")

    item_id = uuid4()
    embedding_dim = get_settings().embedding_dim
    embedding = [0.1] * embedding_dim
    async with get_session() as session:
        await upsert_item_with_embedding(
            session,
            item_id,
            "test content",
            {"source": "test"},
            embedding,
        )
        results = await vector_search(session, embedding, 1, {"source": "test"})

    assert results
    assert results[0][0].id == item_id
