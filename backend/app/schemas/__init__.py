from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    plan: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VideoCreate(BaseModel):
    prompt: str
    duration_s: int = 15


class VideoOut(BaseModel):
    id: str
    prompt: str
    status: str
    url: str | None
    created_at: datetime


class SocialPostCreate(BaseModel):
    platform: str
    content: str
    scheduled_at: datetime | None = None


class WorkflowCreate(BaseModel):
    name: str
    nodes: list[dict] = []
    edges: list[dict] = []

from .campaign import (
    CampaignCreate,
    CampaignOut,
    CampaignFullOut,
    PersonaOut,
    CompetitorInsightOut,
    AngleOut,
    HookOut,
    HeadlineOut,
    CTAOut,
    AdCopyOut,
    CreativeConceptOut,
    VideoScriptOut,
    CampaignScoreOut
)
