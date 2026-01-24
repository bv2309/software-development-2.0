from __future__ import annotations

import threading
from typing import Iterable

from sentence_transformers import CrossEncoder
import structlog
import torch

from ai_accel_api_platform.core.device import get_best_device
from ai_accel_api_platform.settings import get_settings

logger = structlog.get_logger(__name__)

_reranker: CrossEncoder | None = None
_reranker_lock = threading.Lock()


def _load_reranker() -> CrossEncoder:
    settings = get_settings()
    device, device_type = get_best_device(prefer_gpu=settings.prefer_gpu)
    model = CrossEncoder(settings.rerank_model, device=str(device))
    logger.info("reranker_loaded", model=settings.rerank_model, device=device_type)
    return model


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        with _reranker_lock:
            if _reranker is None:
                _reranker = _load_reranker()
    return _reranker


def rerank_results(query: str, results: Iterable[tuple[object, float]]) -> list[tuple[object, float]]:
    settings = get_settings()
    results_list = list(results)
    if not settings.enable_rerank or not results_list:
        return results_list

    model = get_reranker()
    pairs = [(query, getattr(item, "content", "")) for item, _ in results_list]

    with torch.no_grad():
        scores = model.predict(pairs)

    reranked = [(item, float(score)) for (item, _), score in zip(results_list, scores)]
    reranked.sort(key=lambda item: item[1], reverse=True)
    return reranked
