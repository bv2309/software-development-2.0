from __future__ import annotations

from fastapi import APIRouter

from ai_accel_api_platform.api.v1 import (
    routes_auth,
    routes_embeddings,
    routes_health,
    routes_items,
    routes_search,
)

router = APIRouter()
router.include_router(routes_health.router, tags=["health"])
router.include_router(routes_items.router, tags=["items"])
router.include_router(routes_embeddings.router, tags=["embeddings"])
router.include_router(routes_search.router, tags=["search"])
router.include_router(routes_auth.router, tags=["auth"])
