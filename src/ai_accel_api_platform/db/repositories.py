from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_accel_api_platform.core.security import get_password_hash, verify_password
from ai_accel_api_platform.db.models import Item, User


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    user_type: int = 1,
) -> User:
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        user_type=user_type,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(session, username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_name_parts(
    session: AsyncSession,
    username: str,
) -> tuple[str, str, bool] | None:
    result = await session.execute(
        select(User.first_name, User.last_name, User.is_active).where(User.username == username)
    )
    row = result.one_or_none()
    if row is None:
        return None
    first_name, last_name, is_active = row
    return first_name, last_name, is_active


async def ensure_default_user(
    session: AsyncSession,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    user = await get_user_by_username(session, username)
    if user is not None:
        updated = False
        if user.user_type != 0:
            user.user_type = 0
            updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if updated:
            await session.commit()
            await session.refresh(user)
        return user
    legacy_usernames = {"admin", "admin@local", "admin@local.test"}
    if username not in legacy_usernames:
        for legacy_username in legacy_usernames:
            legacy_user = await get_user_by_username(session, legacy_username)
            if legacy_user is not None and legacy_user.user_type == 0:
                legacy_user.username = username
                if first_name and legacy_user.first_name != first_name:
                    legacy_user.first_name = first_name
                if last_name and legacy_user.last_name != last_name:
                    legacy_user.last_name = last_name
                await session.commit()
                await session.refresh(legacy_user)
                return legacy_user
    return await create_user(
        session,
        username,
        password,
        first_name=first_name,
        last_name=last_name,
        user_type=0,
    )


async def upsert_item_with_embedding(
    session: AsyncSession,
    item_id: UUID,
    content: str,
    metadata: dict[str, Any] | None,
    embedding: Iterable[float] | None,
) -> Item:
    result = await session.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        item = Item(id=item_id, content=content, metadata_=metadata, embedding=embedding)
        session.add(item)
    else:
        item.content = content
        item.metadata_ = metadata
        if embedding is not None:
            item.embedding = list(embedding)

    await session.commit()
    await session.refresh(item)
    return item


async def get_item(session: AsyncSession, item_id: UUID) -> Item | None:
    result = await session.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def vector_search(
    session: AsyncSession,
    query_embedding: Iterable[float],
    top_k: int,
    filters: dict[str, Any] | None,
) -> list[tuple[Item, float]]:
    distance = Item.embedding.op("<=>")(list(query_embedding))
    stmt = select(Item, distance.label("distance")).where(Item.embedding.isnot(None))

    if filters:
        stmt = stmt.where(Item.metadata_.contains(filters))

    stmt = stmt.order_by(distance.asc()).limit(top_k)
    result = await session.execute(stmt)
    rows = result.all()
    return [(row[0], 1.0 - float(row[1])) for row in rows]


async def hybrid_search(
    session: AsyncSession,
    query_embedding: Iterable[float],
    top_k: int,
    filters: dict[str, Any] | None,
    text_filter: str | None,
) -> list[tuple[Item, float]]:
    distance = Item.embedding.op("<=>")(list(query_embedding))
    stmt = select(Item, distance.label("distance")).where(Item.embedding.isnot(None))

    if filters:
        stmt = stmt.where(Item.metadata_.contains(filters))
    if text_filter:
        stmt = stmt.where(Item.content.ilike(f"%{text_filter}%"))

    stmt = stmt.order_by(distance.asc()).limit(top_k)
    result = await session.execute(stmt)
    rows = result.all()
    return [(row[0], 1.0 - float(row[1])) for row in rows]
