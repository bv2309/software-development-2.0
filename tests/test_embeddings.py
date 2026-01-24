from __future__ import annotations

import numpy as np

from ai_accel_api_platform.ai import embeddings


class DummyModel:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, **kwargs):
        return np.ones((len(texts), 3), dtype=np.float32)


def test_embed_texts_uses_dummy(monkeypatch):
    monkeypatch.setattr(embeddings, "SentenceTransformer", DummyModel)
    embeddings._embedder = None

    results = embeddings.embed_texts(["hello", "world"])
    assert len(results) == 2
    assert results[0] == [1.0, 1.0, 1.0]
