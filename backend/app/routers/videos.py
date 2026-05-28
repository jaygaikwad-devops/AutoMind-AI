from fastapi import APIRouter
from app.schemas import VideoCreate, VideoOut
from datetime import datetime
import uuid

router = APIRouter()
_DB: list[dict] = []


@router.post("", response_model=VideoOut)
async def create_video(body: VideoCreate):
    v = {"id": str(uuid.uuid4()), "prompt": body.prompt, "status": "queued", "url": None, "created_at": datetime.utcnow()}
    _DB.append(v)
    # TODO: enqueue Celery task -> render video on worker
    return v


@router.get("", response_model=list[VideoOut])
async def list_videos():
    return _DB
