from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ai_accel_api_platform.db.session import get_redis

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests: int, window_seconds: int, use_redis: bool) -> None:
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self.use_redis = use_redis
        self._memory_counts: dict[str, int] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        window_key = int(time.time() // self.window_seconds)
        key = f"{client_ip}:{window_key}"

        if self.use_redis:
            redis = get_redis()
            count = await redis.incr(f"rl:{key}")
            if count == 1:
                await redis.expire(f"rl:{key}", self.window_seconds)
        else:
            count = self._memory_counts.get(key, 0) + 1
            self._memory_counts[key] = count

        if count > self.requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

        return await call_next(request)


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, timeout_seconds: int) -> None:
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout_seconds)
        except TimeoutError:
            return JSONResponse(status_code=504, content={"detail": "Request timeout"})
