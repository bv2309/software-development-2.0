from __future__ import annotations

from fastapi import APIRouter

from ai_accel_api_platform.core.device import get_device_info
from ai_accel_api_platform.core.schemas import HealthResponse
from ai_accel_api_platform.db.session import db_ping
from ai_accel_api_platform.settings import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        device=get_device_info(prefer_gpu=settings.prefer_gpu),
        db_ok=await db_ping(),
    )
