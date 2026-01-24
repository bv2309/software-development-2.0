from __future__ import annotations

from typing import Iterable

from ai_accel_api_platform.core.utils import batch_cosine_similarity


def score_embeddings(
    query_embedding: Iterable[float],
    candidate_embeddings: Iterable[Iterable[float]],
) -> list[float]:
    return batch_cosine_similarity(query_embedding, candidate_embeddings)
