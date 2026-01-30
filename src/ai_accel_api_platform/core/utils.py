from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable
from typing import Any, cast

import numpy as np
import orjson

try:
    from ai_accel_api_platform.cpp.fast_ops import (
        batch_cosine_similarity as cpp_batch_cosine_similarity,
    )
except Exception:  # pragma: no cover - optional extension
    cpp_batch_cosine_similarity = None

_CppBatchFn = Callable[[list[float], list[list[float]]], list[float]]


def batch_cosine_similarity(
    query: Iterable[float], matrix: Iterable[Iterable[float]]
) -> list[float]:
    if cpp_batch_cosine_similarity is not None:
        cpp_fn = cast(_CppBatchFn, cpp_batch_cosine_similarity)
        return list(cpp_fn(list(query), [list(row) for row in matrix]))

    query_vec = np.array(list(query), dtype=np.float32)
    mat = np.array(list(matrix), dtype=np.float32)
    if mat.size == 0:
        return []

    query_norm = np.linalg.norm(query_vec) + 1e-8
    mat_norm = np.linalg.norm(mat, axis=1) + 1e-8
    scores = (mat @ query_vec) / (mat_norm * query_norm)
    return cast(list[float], scores.tolist())


def json_dumps(payload: Any) -> str:
    data: bytes = orjson.dumps(payload)
    return data.decode("utf-8")


def cache_key(prefix: str, parts: Iterable[str]) -> str:
    raw = "|".join(parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def normalize_filters(filters: dict[str, Any] | None) -> dict[str, Any]:
    if not filters:
        return {}
    return {
        str(key): value for key, value in sorted(filters.items(), key=lambda item: str(item[0]))
    }


def build_full_name(first_name: str | None, last_name: str | None) -> str:
    first = (first_name or "").strip()
    last = (last_name or "").strip()
    if not first and not last:
        return ""
    if not first:
        return last
    if not last:
        return first
    return f"{first} {last}"
