from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.database import SessionLocal
from starlette.status import HTTP_201_CREATED
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_204_NO_CONTENT
from app.auth import get_current_user
from app.models import User
from typing import Optional
from datetime import datetime, timezone
#from app.config import CLEANUP_THRESHOLD_DAYS
from app.config import settings
from typing import List
from app.redis import redis_client


router = APIRouter(
    prefix="/links",
    tags=["Links"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/shorten", response_model=schemas.LinkResponse, status_code=HTTP_201_CREATED)
async def create_link(
    link: schemas.LinkCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    try:
        new_link = await crud.create_short_link(db, link, current_user)
        return new_link
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=schemas.LinkResponse)
async def search_link(original_url: str, db: AsyncSession = Depends(get_db)):
    link = await crud.search_link_by_original_url(db, original_url)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link

@router.get("/expired", response_model=List[schemas.LinkResponse])
async def get_expired_links(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    links = await crud.get_expired_links(db, user_id=current_user.id)
    return links

'''
@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")

    await crud.register_click(db, link)
    return RedirectResponse(url=link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
'''

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    cached_url = await redis_client.get(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)

    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")

    await redis_client.set(short_code, link.original_url, ex=3600)
    await crud.register_click(db, link)
    return RedirectResponse(url=link.original_url)
    
@router.get("/{short_code}/stats", response_model=schemas.LinkStats)
async def get_link_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")

    return link

@router.delete("/{short_code}", status_code=HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this link")

    await crud.delete_link(db, short_code)
    return

@router.put("/{short_code}", response_model=schemas.LinkResponse)
async def update_link(
    short_code: str,
    updates: schemas.LinkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this link")

    updated = await crud.update_link(db, short_code, updates)
    return updated

@router.delete("/cleanup", status_code=204)
async def cleanup_unused_links(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    await crud.delete_unused_links(db, settings.CLEANUP_THRESHOLD_DAYS)
    return

