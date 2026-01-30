from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from ai_accel_api_platform.core.utils import cache_key, json_dumps, normalize_filters

CACHE_NAMESPACE_KEY = "search:ns"


def build_search_cache_key(
    namespace: str,
    query: str,
    top_k: int,
    filters: dict[str, Any] | None,
    text_filter: str | None,
) -> str:
    normalized_filters = normalize_filters(filters)
    parts = [
        namespace,
        query.strip().lower(),
        str(top_k),
        json_dumps(normalized_filters),
        (text_filter or "").strip().lower(),
    ]
    return cache_key("search", parts)


async def get_cache_namespace(redis: Redis[str]) -> str:
    namespace: str | None = await redis.get(CACHE_NAMESPACE_KEY)
    if namespace is None:
        namespace = "1"
        await redis.set(CACHE_NAMESPACE_KEY, namespace)
    return namespace


async def bump_cache_namespace(redis: Redis[str]) -> None:
    await redis.incr(CACHE_NAMESPACE_KEY)
