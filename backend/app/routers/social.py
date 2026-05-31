from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import SocialPostCreate
from app.models import SocialPost, User
from app.db import get_db
from app.api.deps import get_current_user
from app.workers.celery_app import publish_post
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/publish")
async def publish(body: SocialPostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_post = SocialPost(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        platform=body.platform,
        content=body.content,
        scheduled_at=body.scheduled_at,
        status="scheduled"
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    
    # Trigger Celery task
    if body.scheduled_at and body.scheduled_at > datetime.utcnow():
        publish_post.apply_async((db_post.id, db_post.platform, db_post.content), eta=body.scheduled_at)
    else:
        publish_post.delay(db_post.id, db_post.platform, db_post.content)

    return {"ok": True, "platform": body.platform, "queued_at": body.scheduled_at, "id": db_post.id}

@router.get("/platforms")
async def platforms(current_user: User = Depends(get_current_user)):
    return ["instagram", "facebook", "linkedin", "tiktok", "youtube", "meta_ads"]
