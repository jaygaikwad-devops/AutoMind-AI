from fastapi import APIRouter, Depends
from app.models import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/overview")
async def overview(current_user: User = Depends(get_current_user)):
    return {
        "posts_today": 1284,
        "leads_24h": 932,
        "viral_score": 92.4,
        "campaigns_running": 7,
        "engagement_rate": 0.087,
    }
