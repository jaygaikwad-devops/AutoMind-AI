"""
/api/v1/marketing — Sprint 3.1A production endpoints.

POST /api/v1/marketing/research      → MarketResearchAgent
POST /api/v1/marketing/persona       → PersonaAgent
POST /api/v1/marketing/hooks         → HookAgent
POST /api/v1/marketing/full-analysis → Research → Persona → Hooks (sequential)

GET  /api/v1/marketing/brand-profiles
POST /api/v1/marketing/brand-profiles
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.models.marketing import BrandProfile
from app.services.billing.credit_service import CreditReservationError
from app.services.agents.runner import AgentRunner
from app.services.agents.market_research_agent import MarketResearchAgent
from app.services.agents.persona_agent import PersonaAgent
from app.services.agents.hook_agent import HookAgent
from app.schemas.marketing import (
    ResearchRequest, PersonaRequest, HookRequest, FullAnalysisRequest,
    ResearchOut, PersonaOut, HookOut, FullAnalysisOut,
    BrandProfileCreate, BrandProfileOut, ValidationOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _credit_error(exc: CreditReservationError):
    raise HTTPException(status_code=402, detail=str(exc))


def _build_research_out(result: dict) -> ResearchOut:
    val = result.get("validation", {})
    return ResearchOut(
        snapshot_id=result["snapshot_id"],
        content_id=result["content_id"],
        job_id=result["job_id"],
        credits_committed=result["credits_committed"],
        quality_score=result.get("quality_score"),
        validation=ValidationOut(**val) if val else None,
        research=result.get("research", {}),
    )


def _build_persona_out(result: dict) -> PersonaOut:
    val = result.get("validation", {})
    return PersonaOut(
        content_id=result["content_id"],
        job_id=result["job_id"],
        credits_committed=result["credits_committed"],
        quality_score=result.get("quality_score"),
        validation=ValidationOut(**val) if val else None,
        personas=result.get("personas", {}),
    )


def _build_hook_out(result: dict) -> HookOut:
    val = result.get("validation", {})
    return HookOut(
        content_id=result["content_id"],
        job_id=result["job_id"],
        credits_committed=result["credits_committed"],
        quality_score=result.get("quality_score"),
        total_hooks=result.get("total_hooks", 0),
        validation=ValidationOut(**val) if val else None,
        hooks=result.get("hooks", {}),
    )


# ── Research endpoint ─────────────────────────────────────────────────────────

@router.post("/research", response_model=ResearchOut, summary="Run market research agent")
async def run_research(
    body: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers MarketResearchAgent.
    Scrapes the website, generates company summary, market position,
    core benefits, competitor summary, keywords, and target audience.
    Persists a ResearchSnapshot + CampaignContent(type=research).
    """
    agent = MarketResearchAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("run_research failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Research generation failed: {exc}")
    return _build_research_out(result)


# ── Persona endpoint ──────────────────────────────────────────────────────────

@router.post("/persona", response_model=PersonaOut, summary="Run persona generation agent")
async def run_persona(
    body: PersonaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers PersonaAgent.
    Accepts either a snapshot_id (from a prior /research call) or inline
    research data.  Generates 3–5 audience personas.
    Persists CampaignContent(type=persona).
    """
    agent = PersonaAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("run_persona failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Persona generation failed: {exc}")
    return _build_persona_out(result)


# ── Hooks endpoint ────────────────────────────────────────────────────────────

@router.post("/hooks", response_model=HookOut, summary="Run hook generation agent")
async def run_hooks(
    body: HookRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers HookAgent.
    Accepts snapshot_id + persona_content_id (from prior calls) or inline data.
    Generates 40 hooks: 10 Curiosity, 10 Pain, 10 Emotional, 10 Authority.
    Persists CampaignContent(type=hooks).
    """
    agent = HookAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("run_hooks failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Hook generation failed: {exc}")
    return _build_hook_out(result)


# ── Full analysis endpoint ────────────────────────────────────────────────────

@router.post("/full-analysis", response_model=FullAnalysisOut, summary="Research → Personas → Hooks")
async def run_full_analysis(
    body: FullAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Runs all three agents sequentially through AgentRunner.
    Total cost: 15 credits (5 + 5 + 5).
    Each stage passes its output into the next stage.
    """
    campaign_id = body.campaign_id
    base_payload = {
        "website_url": body.website_url,
        "product_name": body.product_name,
        "product_description": body.product_description,
        "industry": body.industry,
        "campaign_id": campaign_id,
    }

    # ── Stage 1: Research ────────────────────────────────────────────
    research_agent = MarketResearchAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        research_result = await runner.execute(research_agent, base_payload, campaign_id=campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("full_analysis stage 1 (research) failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Research stage failed: {exc}")

    # ── Stage 2: Persona ─────────────────────────────────────────────
    persona_payload = {
        **base_payload,
        "snapshot_id": research_result["snapshot_id"],
        "research": research_result.get("research", {}),
    }
    persona_agent = PersonaAgent(db, current_user.id)
    runner2 = AgentRunner(db, current_user.id)
    try:
        persona_result = await runner2.execute(persona_agent, persona_payload, campaign_id=campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("full_analysis stage 2 (persona) failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Persona stage failed: {exc}")

    # ── Stage 3: Hooks ───────────────────────────────────────────────
    hook_payload = {
        **base_payload,
        "snapshot_id": research_result["snapshot_id"],
        "persona_content_id": persona_result["content_id"],
        "research": research_result.get("research", {}),
        "personas": persona_result.get("personas", {}),
    }
    hook_agent = HookAgent(db, current_user.id)
    runner3 = AgentRunner(db, current_user.id)
    try:
        hook_result = await runner3.execute(hook_agent, hook_payload, campaign_id=campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("full_analysis stage 3 (hooks) failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Hooks stage failed: {exc}")

    total_credits = (
        research_result["credits_committed"]
        + persona_result["credits_committed"]
        + hook_result["credits_committed"]
    )

    return FullAnalysisOut(
        research=_build_research_out(research_result),
        personas=_build_persona_out(persona_result),
        hooks=_build_hook_out(hook_result),
        total_credits_committed=total_credits,
    )


# ── BrandProfile CRUD ─────────────────────────────────────────────────────────

@router.get("/brand-profiles", response_model=list[BrandProfileOut])
async def list_brand_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BrandProfile)
        .filter(BrandProfile.user_id == current_user.id)
        .order_by(BrandProfile.created_at.desc())
    )
    return result.scalars().all()


@router.post("/brand-profiles", response_model=BrandProfileOut, status_code=201)
async def create_brand_profile(
    body: BrandProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # If setting as default, unset all others
    if body.is_default:
        existing = await db.execute(
            select(BrandProfile).filter(BrandProfile.user_id == current_user.id, BrandProfile.is_default == 1)
        )
        for bp in existing.scalars().all():
            bp.is_default = 0
        await db.commit()

    profile = BrandProfile(
        user_id=current_user.id,
        brand_name=body.brand_name,
        website_url=body.website_url,
        industry=body.industry,
        tone=body.tone,
        target_audience=body.target_audience,
        brand_colors=body.brand_colors,
        is_default=1 if body.is_default else 0,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.delete("/brand-profiles/{profile_id}", status_code=204)
async def delete_brand_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BrandProfile).filter(
            BrandProfile.id == profile_id,
            BrandProfile.user_id == current_user.id,
        )
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    await db.delete(profile)
    await db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# Sprint 3.1C — Content Intelligence Endpoints
# ══════════════════════════════════════════════════════════════════════════════

from app.services.agents.caption_agent import CaptionAgent
from app.services.agents.hashtag_agent import HashtagAgent
from app.services.agents.adcopy_agent import AdCopyAgent
from app.services.agents.seo_agent import SEOAgent
from app.services.agents.cta_agent import CTAAgent
from pydantic import BaseModel as PydanticBaseModel


# ── Request schemas (3.1C) ────────────────────────────────────────────────────

class CaptionRequest(PydanticBaseModel):
    snapshot_id: str | None = None
    persona_content_id: str | None = None
    hooks_content_id: str | None = None
    brand_profile_id: str | None = None
    research: dict | None = None
    personas: dict | None = None
    hooks: dict | None = None
    campaign_id: str | None = None
    product_name: str | None = None

class HashtagRequest2(PydanticBaseModel):
    snapshot_id: str | None = None
    platform: str = "instagram"
    industry: str | None = None
    research: dict | None = None
    campaign_id: str | None = None
    product_name: str | None = None

class AdCopyRequest(PydanticBaseModel):
    snapshot_id: str | None = None
    persona_content_id: str | None = None
    hooks_content_id: str | None = None
    industry: str | None = None
    research: dict | None = None
    personas: dict | None = None
    hooks: dict | None = None
    campaign_id: str | None = None
    product_name: str | None = None

class SEORequest(PydanticBaseModel):
    snapshot_id: str | None = None
    industry: str | None = None
    research: dict | None = None
    campaign_id: str | None = None
    product_name: str | None = None

class CTARequest(PydanticBaseModel):
    persona_content_id: str | None = None
    adcopy_content_id: str | None = None
    brand_profile_id: str | None = None
    personas: dict | None = None
    adcopy: dict | None = None
    campaign_id: str | None = None

class FullContentBundleRequest(PydanticBaseModel):
    website_url: str | None = None
    product_name: str
    product_description: str | None = None
    industry: str | None = None
    brand_profile_id: str | None = None
    campaign_id: str | None = None


# ── Caption endpoint ──────────────────────────────────────────────────────────

@router.post("/captions", summary="Generate platform-specific captions")
async def run_captions(
    body: CaptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = CaptionAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {exc}")
    return {"content_id": result["content_id"], "job_id": result["job_id"], "credits_committed": result["credits_committed"], "quality_score": result.get("quality_score"), "captions": result.get("captions", {})}


# ── Hashtag endpoint ──────────────────────────────────────────────────────────

@router.post("/hashtags", summary="Generate categorized hashtags")
async def run_hashtags(
    body: HashtagRequest2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = HashtagAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Hashtag generation failed: {exc}")
    return {"content_id": result["content_id"], "job_id": result["job_id"], "credits_committed": result["credits_committed"], "quality_score": result.get("quality_score"), "total_hashtags": result.get("total_hashtags", 0), "hashtags": result.get("hashtags", {})}


# ── Ad Copy endpoint ──────────────────────────────────────────────────────────

@router.post("/adcopy", summary="Generate multi-framework ad copy")
async def run_adcopy(
    body: AdCopyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = AdCopyAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ad copy generation failed: {exc}")
    return {"content_id": result["content_id"], "job_id": result["job_id"], "credits_committed": result["credits_committed"], "quality_score": result.get("quality_score"), "adcopy": result.get("adcopy", {})}


# ── SEO endpoint ──────────────────────────────────────────────────────────────

@router.post("/seo", summary="Generate SEO content package")
async def run_seo(
    body: SEORequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = SEOAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SEO generation failed: {exc}")
    return {"content_id": result["content_id"], "job_id": result["job_id"], "credits_committed": result["credits_committed"], "quality_score": result.get("quality_score"), "seo": result.get("seo", {})}


# ── CTA endpoint ──────────────────────────────────────────────────────────────

@router.post("/cta", summary="Generate categorized CTAs")
async def run_cta(
    body: CTARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = CTAAgent(db, current_user.id)
    runner = AgentRunner(db, current_user.id)
    try:
        result = await runner.execute(agent, body.model_dump(), campaign_id=body.campaign_id)
    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"CTA generation failed: {exc}")
    return {"content_id": result["content_id"], "job_id": result["job_id"], "credits_committed": result["credits_committed"], "quality_score": result.get("quality_score"), "total_ctas": result.get("total_ctas", 0), "ctas": result.get("ctas", {})}


# ── Full Content Bundle ───────────────────────────────────────────────────────

@router.post("/full-content-bundle", summary="Research → Persona → Hooks → Captions → Hashtags → AdCopy → SEO → CTA")
async def run_full_content_bundle(
    body: FullContentBundleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sequences all 8 agents. Each step feeds into the next.
    Total cost: 5+5+5+5+3+8+5+3 = 39 credits (individual pricing).
    Returns all generated content in one response.
    """
    campaign_id = body.campaign_id
    base = {
        "website_url": body.website_url,
        "product_name": body.product_name,
        "product_description": body.product_description,
        "industry": body.industry,
        "brand_profile_id": body.brand_profile_id,
        "campaign_id": campaign_id,
    }

    results = {}
    total_credits = 0

    # Helper to run an agent and accumulate
    async def _run(agent_cls, payload):
        nonlocal total_credits
        agent = agent_cls(db, current_user.id)
        runner = AgentRunner(db, current_user.id)
        r = await runner.execute(agent, payload, campaign_id=campaign_id)
        total_credits += r.get("credits_committed", 0)
        return r

    try:
        # 1. Research
        results["research"] = await _run(MarketResearchAgent, base)

        # 2. Persona
        results["persona"] = await _run(PersonaAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "research": results["research"].get("research", {}),
        })

        # 3. Hooks
        results["hooks"] = await _run(HookAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "persona_content_id": results["persona"]["content_id"],
            "research": results["research"].get("research", {}),
            "personas": results["persona"].get("personas", {}),
        })

        # 4. Captions
        results["captions"] = await _run(CaptionAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "persona_content_id": results["persona"]["content_id"],
            "hooks_content_id": results["hooks"]["content_id"],
            "research": results["research"].get("research", {}),
            "personas": results["persona"].get("personas", {}),
            "hooks": results["hooks"].get("hooks", {}),
        })

        # 5. Hashtags
        results["hashtags"] = await _run(HashtagAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "research": results["research"].get("research", {}),
            "platform": "instagram",
        })

        # 6. Ad Copy
        results["adcopy"] = await _run(AdCopyAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "persona_content_id": results["persona"]["content_id"],
            "hooks_content_id": results["hooks"]["content_id"],
            "research": results["research"].get("research", {}),
            "personas": results["persona"].get("personas", {}),
            "hooks": results["hooks"].get("hooks", {}),
        })

        # 7. SEO
        results["seo"] = await _run(SEOAgent, {
            **base,
            "snapshot_id": results["research"]["snapshot_id"],
            "research": results["research"].get("research", {}),
        })

        # 8. CTA
        results["cta"] = await _run(CTAAgent, {
            **base,
            "persona_content_id": results["persona"]["content_id"],
            "adcopy_content_id": results["adcopy"]["content_id"],
        })

    except CreditReservationError as exc:
        _credit_error(exc)
    except Exception as exc:
        logger.error("full_content_bundle failed at stage: %s", exc)
        # Return partial results
        return {
            "status": "partial",
            "completed": list(results.keys()),
            "error": str(exc),
            "total_credits_committed": total_credits,
            "results": {k: {"content_id": v.get("content_id"), "quality_score": v.get("quality_score")} for k, v in results.items()},
        }

    # Emit bundle completion event
    from app.models.activity import ActivityEvent
    bundle_event = ActivityEvent(
        user_id=current_user.id,
        event="content_bundle_completed",
        agent="content_bundle_orchestrator",
        credits_used=total_credits,
        campaign_id=campaign_id,
        metadata_json={
            "agents_completed": list(results.keys()),
            "total_credits": total_credits,
            "quality_scores": {k: v.get("quality_score") for k, v in results.items()},
        },
    )
    db.add(bundle_event)
    await db.commit()

    return {
        "status": "completed",
        "total_credits_committed": total_credits,
        "agents_completed": list(results.keys()),
        "quality_scores": {k: v.get("quality_score") for k, v in results.items()},
        "content_ids": {k: v.get("content_id") for k, v in results.items()},
        "research": results["research"].get("research", {}),
        "personas": results["persona"].get("personas", {}),
        "hooks": results["hooks"].get("hooks", {}),
        "captions": results["captions"].get("captions", {}),
        "hashtags": results["hashtags"].get("hashtags", {}),
        "adcopy": results["adcopy"].get("adcopy", {}),
        "seo": results["seo"].get("seo", {}),
        "ctas": results["cta"].get("ctas", {}),
    }
