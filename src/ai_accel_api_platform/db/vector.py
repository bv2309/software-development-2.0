from __future__ import annotations

from typing import Any, Optional

from redis.asyncio import Redis

from ai_accel_api_platform.core.utils import cache_key, json_dumps, normalize_filters

CACHE_NAMESPACE_KEY = "search:ns"


def build_search_cache_key(
    namespace: str,
    query: str,
    top_k: int,
    filters: Optional[dict[str, Any]],
    text_filter: Optional[str],
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


async def get_cache_namespace(redis: Redis) -> str:
    namespace = await redis.get(CACHE_NAMESPACE_KEY)
    if namespace is None:
        namespace = "1"
        await redis.set(CACHE_NAMESPACE_KEY, namespace)
    return namespace


async def bump_cache_namespace(redis: Redis) -> None:
    await redis.incr(CACHE_NAMESPACE_KEY)
