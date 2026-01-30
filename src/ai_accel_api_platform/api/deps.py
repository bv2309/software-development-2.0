from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_accel_api_platform.core.security import (
    credentials_exception,
    decode_subject_from_token,
    oauth2_scheme,
)
from ai_accel_api_platform.db.models import User
from ai_accel_api_platform.db.repositories import get_user_by_username
from ai_accel_api_platform.db.session import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    username = decode_subject_from_token(token)
    user = await get_user_by_username(session, username)
    if user is None or not user.is_active:
        raise credentials_exception()
    return user
