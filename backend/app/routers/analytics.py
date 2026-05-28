from fastapi import APIRouter

router = APIRouter()


@router.get("/overview")
async def overview():
    return {
        "posts_today": 1284,
        "leads_24h": 932,
        "viral_score": 92.4,
        "campaigns_running": 7,
        "engagement_rate": 0.087,
    }
