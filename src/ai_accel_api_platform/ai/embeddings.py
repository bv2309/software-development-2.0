from __future__ import annotations

import threading
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer
import structlog
import torch

from ai_accel_api_platform.core.device import get_best_device
from ai_accel_api_platform.settings import get_settings

logger = structlog.get_logger(__name__)

_embedder: SentenceTransformer | None = None
_embedder_lock = threading.Lock()


def _maybe_quantize(model: SentenceTransformer, enable: bool, device_type: str) -> SentenceTransformer:
    if not enable:
        return model
    if device_type != "cpu":
        logger.info("quantization_skipped", reason="non_cpu")
        return model
    try:
        model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
        logger.info("quantization_enabled")
    except Exception as exc:
        logger.warning("quantization_failed", error=str(exc))
    return model


def _maybe_compile(model: SentenceTransformer, enable: bool) -> SentenceTransformer:
    if not enable:
        return model
    if not hasattr(torch, "compile"):
        logger.info("torch_compile_unavailable")
        return model
    try:
        model = torch.compile(model)
        logger.info("torch_compile_enabled")
    except Exception as exc:
        logger.warning("torch_compile_failed", error=str(exc))
    return model


def _load_model() -> SentenceTransformer:
    settings = get_settings()
    device, device_type = get_best_device(prefer_gpu=settings.prefer_gpu)
    model = SentenceTransformer(settings.embedding_model, device=str(device))
    model = _maybe_quantize(model, settings.embed_quantize, device_type)
    model = _maybe_compile(model, settings.embed_compile)
    logger.info("embedding_model_loaded", model=settings.embedding_model, device=device_type)
    return model


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        with _embedder_lock:
            if _embedder is None:
                _embedder = _load_model()
    return _embedder


def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    settings = get_settings()
    model = get_embedder()
    with torch.no_grad():
        embeddings = model.encode(
            list(texts),
            batch_size=settings.embed_batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()
    return [emb.tolist() for emb in embeddings]
