from fastapi import APIRouter
from app.schemas import WorkflowCreate

router = APIRouter()
_DB: list[dict] = []


@router.post("")
async def create(body: WorkflowCreate):
    wf = body.model_dump() | {"id": str(len(_DB) + 1)}
    _DB.append(wf)
    return wf


@router.get("")
async def list_workflows():
    return _DB
