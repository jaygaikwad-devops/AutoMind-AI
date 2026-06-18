"""
Pydantic schemas for the /api/v1/marketing/* endpoints.
"""
from __future__ import annotations
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Any, Optional
from datetime import datetime


# ── Request bodies ──────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    website_url: Optional[str] = None
    product_name: str
    product_description: Optional[str] = None
    industry: Optional[str] = None
    campaign_id: Optional[str] = None  # link to an existing Campaign row


class PersonaRequest(BaseModel):
    snapshot_id: Optional[str] = None           # from a prior /research call
    research: Optional[dict[str, Any]] = None   # or inline research dict
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_id: Optional[str] = None


class HookRequest(BaseModel):
    snapshot_id: Optional[str] = None
    persona_content_id: Optional[str] = None    # CampaignContent.id with type=persona
    research: Optional[dict[str, Any]] = None
    personas: Optional[dict[str, Any]] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    campaign_id: Optional[str] = None


class FullAnalysisRequest(BaseModel):
    website_url: Optional[str] = None
    product_name: str
    product_description: Optional[str] = None
    industry: Optional[str] = None
    campaign_id: Optional[str] = None


# ── Response bodies ──────────────────────────────────────────────────────────

class ValidationOut(BaseModel):
    quality_score: int
    issues: list[str] = []
    recommendations: list[str] = []
    passed: bool


class ResearchOut(BaseModel):
    snapshot_id: str
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    research: dict[str, Any]


class PersonaOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    personas: dict[str, Any]


class HookOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    total_hooks: int
    validation: Optional[ValidationOut] = None
    hooks: dict[str, Any]


class FullAnalysisOut(BaseModel):
    research: ResearchOut
    personas: PersonaOut
    hooks: HookOut
    total_credits_committed: int


# ── BrandProfile ─────────────────────────────────────────────────────────────

class BrandProfileCreate(BaseModel):
    brand_name: str
    website_url: Optional[str] = None
    industry: Optional[str] = None
    tone: Optional[list[str]] = None
    target_audience: Optional[str] = None
    brand_colors: Optional[dict[str, str]] = None
    is_default: bool = False


class BrandProfileOut(BaseModel):
    id: str
    brand_name: str
    website_url: Optional[str] = None
    industry: Optional[str] = None
    tone: Optional[list[str]] = None
    target_audience: Optional[str] = None
    brand_colors: Optional[dict[str, str]] = None
    is_default: int
    created_at: datetime

    class Config:
        from_attributes = True
