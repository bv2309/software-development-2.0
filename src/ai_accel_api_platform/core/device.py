from __future__ import annotations

from typing import Any, Tuple

import torch


def get_best_device(prefer_gpu: bool = True) -> Tuple[torch.device, str]:
    if prefer_gpu and torch.cuda.is_available():
        return torch.device("cuda"), "cuda"
    if prefer_gpu and torch.backends.mps.is_available():
        return torch.device("mps"), "mps"
    return torch.device("cpu"), "cpu"


def get_device_info(prefer_gpu: bool = True) -> dict[str, Any]:
    device, device_type = get_best_device(prefer_gpu=prefer_gpu)

    if device_type == "cuda":
        name = torch.cuda.get_device_name(0)
    elif device_type == "mps":
        name = "Apple MPS"
    else:
        name = "CPU"

    return {
        "device": device_type,
        "device_name": name,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "mps_available": torch.backends.mps.is_available(),
        "preferred": prefer_gpu,
        "torch_device": str(device),
    }
