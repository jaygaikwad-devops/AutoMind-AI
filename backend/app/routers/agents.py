from fastapi import APIRouter

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
async def list_agents():
    return AGENTS


@router.post("/{kind}/run")
async def run_agent(kind: str, payload: dict | None = None):
    return {"agent": kind, "status": "dispatched", "task_id": "demo-task"}
