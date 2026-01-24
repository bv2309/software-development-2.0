from __future__ import annotations

from contextlib import asynccontextmanager

from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ai_accel_api_platform.settings import get_settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_redis: AsyncRedis | None = None
_redis_sync: Redis | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_pre_ping=True,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _sessionmaker


@asynccontextmanager
async def get_session() -> AsyncSession:
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        await session.close()


async def db_ping() -> bool:
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_redis() -> AsyncRedis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def get_sync_redis() -> Redis:
    global _redis_sync
    if _redis_sync is None:
        settings = get_settings()
        _redis_sync = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_sync
