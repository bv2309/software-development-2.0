from __future__ import annotations

from typing import Any, Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_accel_api_platform.core.security import get_password_hash, verify_password
from ai_accel_api_platform.db.models import Item, User


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, username: str, password: str) -> User:
    user = User(username=username, hashed_password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(session, username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def ensure_default_user(session: AsyncSession, username: str, password: str) -> User:
    user = await get_user_by_username(session, username)
    if user is not None:
        return user
    return await create_user(session, username, password)


async def upsert_item_with_embedding(
    session: AsyncSession,
    item_id: UUID,
    content: str,
    metadata: Optional[dict[str, Any]],
    embedding: Optional[Iterable[float]],
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


async def get_item(session: AsyncSession, item_id: UUID) -> Optional[Item]:
    result = await session.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def vector_search(
    session: AsyncSession,
    query_embedding: Iterable[float],
    top_k: int,
    filters: Optional[dict[str, Any]],
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
    filters: Optional[dict[str, Any]],
    text_filter: Optional[str],
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
