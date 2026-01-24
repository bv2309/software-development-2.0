from __future__ import annotations

import torch

from ai_accel_api_platform.core.device import get_best_device


def test_get_best_device_prefers_cuda(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)

    device, name = get_best_device(prefer_gpu=True)
    assert device.type == "cuda"
    assert name == "cuda"


def test_get_best_device_falls_back_to_mps(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)

    device, name = get_best_device(prefer_gpu=True)
    assert device.type == "mps"
    assert name == "mps"


def test_get_best_device_cpu(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)

    device, name = get_best_device(prefer_gpu=True)
    assert device.type == "cpu"
    assert name == "cpu"


def test_get_best_device_respects_prefer_gpu_false(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)

    device, name = get_best_device(prefer_gpu=False)
    assert device.type == "cpu"
    assert name == "cpu"
