"""
VideoScriptAgent — MVP Launch

Generates video scripts for: UGC, Product Demo, Instagram Reel, Short-form Ad.
Consumes: ResearchSnapshot, Personas, Hooks, Captions, Ad Copy.
Persists: CampaignContent(content_type="video_script")
Credit cost: 8
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.future import select

from app.models.marketing import ResearchSnapshot, CampaignContent, BrandProfile
from app.models.activity import ActivityEvent
from app.services.llm.provider_registry import get_provider
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_SCRIPT_SYSTEM = """You are a viral video scriptwriter specializing in short-form marketing content.
Generate 4 video scripts tailored for different formats.

FORMATS:
1. UGC (User-Generated Content): Casual, first-person, authentic feel. 30-60 seconds.
2. Product Demo: Feature-focused, clear value proposition. 15-30 seconds.
3. Instagram Reel: Trend-aware, hook-first, visual. 15-30 seconds.
4. Short-form Ad: Direct response, problem-solution, strong CTA. 15-30 seconds.

Each script must include:
- hook (first 3 seconds — must stop the scroll)
- body (main content)
- cta (closing call-to-action)
- visual_notes (what should appear on screen)
- duration_seconds (estimated length)

Return ONLY valid JSON:
{
  "scripts": {
    "ugc": {"hook": "...", "body": "...", "cta": "...", "visual_notes": "...", "duration_seconds": 45},
    "product_demo": {"hook": "...", "body": "...", "cta": "...", "visual_notes": "...", "duration_seconds": 25},
    "instagram_reel": {"hook": "...", "body": "...", "cta": "...", "visual_notes": "...", "duration_seconds": 20},
    "short_ad": {"hook": "...", "body": "...", "cta": "...", "visual_notes": "...", "duration_seconds": 20}
  }
}"""


class VideoScriptAgent(BaseAgent):

    credit_cost: int = 8
    event_type: str = "video_script_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        research = await self._resolve_research(payload)
        personas = await self._resolve_content(payload, "persona_content_id", "persona")
        hooks = await self._resolve_content(payload, "hooks_content_id", "hooks")
        captions = await self._resolve_content(payload, "captions_content_id", "caption")
        brand = await self._resolve_brand(payload)

        context = f"""RESEARCH:\n{json.dumps(research, indent=2)[:1200]}

PERSONAS:\n{json.dumps(personas, indent=2)[:800]}

HOOKS (best ones for video openers):\n{json.dumps(hooks, indent=2)[:600]}

CAPTIONS (for tone reference):\n{json.dumps(captions, indent=2)[:600]}

BRAND: {brand.get('brand_name', 'the product')}
TONE: {json.dumps(brand.get('tone', ['energetic']))}"""

        provider = get_provider()
        scripts = provider.generate_json(
            system=_SCRIPT_SYSTEM,
            user=f"Generate 4 video scripts:\n\n{context}",
        )

        return {"video_scripts": scripts, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("video_scripts", {}), "video scripts")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["video_scripts"] = retry["video_scripts"]
                validation = validate_content(result["video_scripts"], "video scripts")
            except Exception:
                pass
        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = result.get("validation", {})
        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="video_script",
            content_json=result.get("video_scripts", {}),
            quality_score=result.get("quality_score"),
            validation_json={"issues": validation.get("issues", []), "recommendations": validation.get("recommendations", [])},
            validation_passed=1 if validation.get("passed") else 0,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        result["content_id"] = content.id
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        event = ActivityEvent(
            user_id=self.user_id, event=self.event_type, agent="video_script_agent",
            credits_used=self.credit_cost, job_id=job_id, campaign_id=self._campaign_id,
            metadata_json={"content_id": result.get("content_id"), "quality_score": result.get("quality_score")},
        )
        self.db.add(event)
        await self.db.commit()

    async def _resolve_research(self, payload: dict) -> dict:
        if "research" in payload and isinstance(payload["research"], dict):
            return payload["research"]
        sid = payload.get("snapshot_id")
        if sid:
            r = await self.db.execute(select(ResearchSnapshot).filter(ResearchSnapshot.id == sid))
            s = r.scalars().first()
            if s:
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "target_audience_summary": s.target_audience_summary, "product_name": s.product_name}
        return {"product_name": payload.get("product_name", "")}

    async def _resolve_content(self, payload: dict, key: str, content_type: str) -> dict:
        if content_type in payload and isinstance(payload[content_type], dict):
            return payload[content_type]
        cid = payload.get(key)
        if cid:
            r = await self.db.execute(select(CampaignContent).filter(CampaignContent.id == cid, CampaignContent.content_type == content_type))
            c = r.scalars().first()
            if c:
                return c.content_json or {}
        return {}

    async def _resolve_brand(self, payload: dict) -> dict:
        bid = payload.get("brand_profile_id")
        if bid:
            r = await self.db.execute(select(BrandProfile).filter(BrandProfile.id == bid))
            bp = r.scalars().first()
            if bp:
                return {"brand_name": bp.brand_name, "tone": bp.tone or ["energetic"]}
        r = await self.db.execute(select(BrandProfile).filter(BrandProfile.user_id == self.user_id, BrandProfile.is_default == 1))
        bp = r.scalars().first()
        if bp:
            return {"brand_name": bp.brand_name, "tone": bp.tone or ["energetic"]}
        return {"brand_name": "the product", "tone": ["energetic"]}
