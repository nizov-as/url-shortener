import random
import string
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import delete, select
from app.redis import redis_client


SHORT_CODE_LENGTH = 6
CACHE_TTL_SECONDS = 60 * 60 


def generate_short_code(length: int = SHORT_CODE_LENGTH) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def get_link_by_alias(db: AsyncSession, alias: str):
    result = await db.execute(select(models.Link).where(models.Link.custom_alias == alias))
    return result.scalars().first()


async def get_link_by_code(db: AsyncSession, code: str):
    result = await db.execute(select(models.Link).where(models.Link.short_code == code))
    return result.scalars().first()


async def create_short_link(db: AsyncSession, link: schemas.LinkCreate, user: Optional[models.User]) -> models.Link:
    if link.custom_alias:
        existing = await get_link_by_alias(db, link.custom_alias)
        if existing:
            raise ValueError("Custom alias already exists")

        short_code = link.custom_alias
    else:
        while True:
            short_code = generate_short_code()
            existing = await get_link_by_code(db, short_code)
            if not existing:
                break

    new_link = models.Link(
        original_url=str(link.original_url),
        short_code=short_code,
        custom_alias=link.custom_alias,
        expires_at=link.expires_at,
        user_id=user.id if user else None
    )

    db.add(new_link)
    try:
        await db.commit()
        await db.refresh(new_link)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Failed to create link due to duplicate")

    return new_link

async def register_click(db: AsyncSession, link: models.Link):
    link.click_count += 1
    link.last_clicked = datetime.utcnow()
    db.add(link)
    await db.commit()

async def delete_link(db: AsyncSession, short_code: str):
    link = await get_link_by_code(db, short_code)
    if not link:
        return None

    await db.delete(link)
    await db.commit()
    await redis_client.delete(short_code)
    return link

async def update_link(db: AsyncSession, short_code: str, updates: schemas.LinkUpdate):
    link = await get_link_by_code(db, short_code)
    if not link:
        return None
    if updates.original_url is not None:
        link.original_url = str(updates.original_url)
    if updates.expires_at is not None:
        link.expires_at = updates.expires_at
    db.add(link)
    await db.commit()
    await db.refresh(link)
    await redis_client.delete(short_code)
    return link

async def search_link_by_original_url(db: AsyncSession, original_url: str):
    result = await db.execute(
        select(models.Link).where(models.Link.original_url == original_url)
    )
    return result.scalars().first()

async def delete_unused_links(db: AsyncSession, threshold_days: int):
    threshold_date = datetime.utcnow() - timedelta(days=threshold_days)

    stmt = delete(models.Link).where(
        models.Link.last_clicked < threshold_date
    )

    await db.execute(stmt)
    await db.commit()

async def get_expired_links(db: AsyncSession, user_id: int = None):
    query = select(models.Link).where(
        models.Link.expires_at.isnot(None),
        models.Link.expires_at < datetime.utcnow()
    )

    if user_id:
        query = query.where(models.Link.user_id == user_id)

    result = await db.execute(query)
    return result.scalars().all()

async def get_link_with_cache(db: AsyncSession, short_code: str):
    cached_url = await redis_client.get(short_code)
    if cached_url:
        return cached_url

    result = await db.execute(select(models.Link).where(models.Link.short_code == short_code))
    link = result.scalars().first()
    if link:
        await redis_client.set(short_code, link.original_url, ex=CACHE_TTL_SECONDS)
    return link