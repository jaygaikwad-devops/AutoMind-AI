from fastapi import APIRouter, Depends
from app.models import User
from app.api.deps import get_current_user

router = APIRouter()

AGENTS = [
    {"kind": "video", "name": "Video Agent"},
    {"kind": "content", "name": "Content Agent"},
    {"kind": "analytics", "name": "Analytics Agent"},
    {"kind": "publishing", "name": "Publishing Agent"},
    {"kind": "leadgen", "name": "Lead Generation Agent"},
    {"kind": "adops", "name": "Ad Optimization Agent"},
]

@router.get("")
async def list_agents(current_user: User = Depends(get_current_user)):
    return AGENTS

@router.post("/{kind}/run")
async def run_agent(kind: str, payload: dict | None = None, current_user: User = Depends(get_current_user)):
    return {"agent": kind, "status": "dispatched", "task_id": "demo-task", "user_id": current_user.id}
