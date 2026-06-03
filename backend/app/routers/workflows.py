from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import WorkflowCreate
from app.models import Workflow, User
from app.db import get_db
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.post("")
async def create(body: WorkflowCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_wf = Workflow(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=body.name,
        nodes=body.nodes,
        edges=body.edges
    )
    db.add(db_wf)
    await db.commit()
    await db.refresh(db_wf)
    return db_wf

@router.get("")
async def list_workflows(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).filter(Workflow.user_id == current_user.id))
    workflows = result.scalars().all()
    return workflows

@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.workers.celery_app import execute_workflow_task
    result = await db.execute(select(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == current_user.id))
    wf = result.scalars().first()
    if not wf:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    execute_workflow_task.delay(workflow_id)
    return {"status": "started", "workflow_id": workflow_id}
