from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_accel_api_platform.api.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    TimeoutMiddleware,
)
from ai_accel_api_platform.api.v1 import router as v1_router
from ai_accel_api_platform.db.repositories import ensure_default_user
from ai_accel_api_platform.db.session import get_session
from ai_accel_api_platform.grpc_server import start_grpc_server
from ai_accel_api_platform.logging import configure_logging
from ai_accel_api_platform.settings import get_settings
from ai_accel_api_platform.telemetry.metrics import MetricsMiddleware
from ai_accel_api_platform.telemetry.metrics import router as metrics_router
from ai_accel_api_platform.telemetry.tracing import setup_tracing

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title="AI Accel API Platform", version="0.1.0")

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(TimeoutMiddleware, timeout_seconds=settings.request_timeout_seconds)
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
        use_redis=settings.app_env == "production",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router, prefix="/v1")
    app.include_router(metrics_router)

    if settings.enable_tracing:
        setup_tracing(app)

    @app.on_event("startup")
    async def startup() -> None:
        try:
            async with get_session() as session:
                await ensure_default_user(
                    session,
                    settings.default_admin_username,
                    settings.default_admin_password,
                    settings.default_admin_first_name,
                    settings.default_admin_last_name,
                )
        except Exception as exc:
            logger.warning("default_user_init_failed", error=str(exc))
        if settings.enable_grpc:
            start_grpc_server()

    return app


app = create_app()
