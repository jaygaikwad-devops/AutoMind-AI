from fastapi import APIRouter
from app.schemas import SocialPostCreate

router = APIRouter()


@router.post("/publish")
async def publish(body: SocialPostCreate):
    # TODO: enqueue platform publisher worker
    return {"ok": True, "platform": body.platform, "queued_at": body.scheduled_at}


@router.get("/platforms")
async def platforms():
    return ["instagram", "facebook", "linkedin", "tiktok", "youtube", "meta_ads"]
