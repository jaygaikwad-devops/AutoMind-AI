from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.models.campaign import CampaignJob
from app.api.deps import get_current_user
from app.db import get_db
from app.services.billing.credit_service import CreditService, CreditReservationError
from app.core.constants import AGENT_COSTS, JOB_STATUS
import uuid
from app.workers.celery_app import execute_agent_task

router = APIRouter()

AGENTS = [
    {"kind": "creative_studio", "name": "Creative Studio"},
    {"kind": "content_strategist", "name": "Content Strategist"},
    {"kind": "growth_intelligence", "name": "Growth Intelligence"},
    {"kind": "media_buyer", "name": "Media Buyer"},
    {"kind": "distribution_engine", "name": "Distribution Engine"},
]

@router.get("")
async def list_agents(current_user: User = Depends(get_current_user)):
    return AGENTS

@router.post("/{kind}/run")
async def run_agent(
    kind: str, 
    payload: dict | None = None, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if kind not in AGENT_COSTS:
        raise HTTPException(status_code=400, detail="Unknown agent kind")
        
    amount = AGENT_COSTS[kind]
    job_id = str(uuid.uuid4())
    
    try:
        await CreditService.reserve_credits(db, current_user.id, amount, job_id=None)
    except CreditReservationError as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    new_job = CampaignJob(
        id=job_id,
        user_id=current_user.id,
        job_type=kind,
        status=JOB_STATUS["PENDING"],
        credits_reserved=amount
    )
    db.add(new_job)
    await db.commit()
    
    execute_agent_task.delay(kind, job_id, payload)
    
    return {
        "agent": kind, 
        "status": JOB_STATUS["PENDING"], 
        "task_id": job_id, 
        "user_id": current_user.id
    }
