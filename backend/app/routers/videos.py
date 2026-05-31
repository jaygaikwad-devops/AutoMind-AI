from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import VideoCreate, VideoOut
from app.models import Video, User
from app.db import get_db
from app.api.deps import get_current_user
from app.workers.celery_app import render_video
import uuid

router = APIRouter()

@router.post("", response_model=VideoOut)
async def create_video(body: VideoCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_video = Video(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        prompt=body.prompt,
        status="queued",
        duration_s=body.duration_s
    )
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    
    # Trigger Celery task
    render_video.delay(db_video.id, db_video.prompt)
    
    return db_video

@router.get("", response_model=list[VideoOut])
async def list_videos(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).filter(Video.user_id == current_user.id).order_by(Video.created_at.desc()))
    videos = result.scalars().all()
    return videos
