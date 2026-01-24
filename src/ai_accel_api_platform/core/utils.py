from __future__ import annotations

import hashlib
from typing import Any, Iterable, Optional

import numpy as np
import orjson

try:
    from ai_accel_api_platform.cpp.fast_ops import batch_cosine_similarity as cpp_batch_cosine_similarity
except Exception:  # pragma: no cover - optional extension
    cpp_batch_cosine_similarity = None


def batch_cosine_similarity(query: Iterable[float], matrix: Iterable[Iterable[float]]) -> list[float]:
    if cpp_batch_cosine_similarity is not None:
        return list(cpp_batch_cosine_similarity(list(query), [list(row) for row in matrix]))

    query_vec = np.array(list(query), dtype=np.float32)
    mat = np.array(list(matrix), dtype=np.float32)
    if mat.size == 0:
        return []

    query_norm = np.linalg.norm(query_vec) + 1e-8
    mat_norm = np.linalg.norm(mat, axis=1) + 1e-8
    scores = (mat @ query_vec) / (mat_norm * query_norm)
    return scores.tolist()


def json_dumps(payload: Any) -> str:
    return orjson.dumps(payload).decode("utf-8")


def cache_key(prefix: str, parts: Iterable[str]) -> str:
    raw = "|".join(parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def normalize_filters(filters: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not filters:
        return {}
    return {str(key): value for key, value in sorted(filters.items(), key=lambda item: str(item[0]))}
