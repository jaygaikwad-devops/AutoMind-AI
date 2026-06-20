"""
CaptionAgent — Sprint 3.1C

Generates platform-specific captions for Instagram, LinkedIn, Facebook, TikTok, YouTube Shorts.
Consumes: ResearchSnapshot, Personas, Hooks, BrandProfile.
Persists: CampaignContent(content_type="caption")
Credit cost: 5
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

_CAPTION_SYSTEM = """You are an expert social media copywriter creating platform-native content.
Generate one unique caption per platform, tailored to each platform's norms.

PLATFORM GUIDELINES:
- Instagram: Casual, emoji-rich, max 2200 chars. Hook in first line, CTA at end.
- LinkedIn: Professional, insight-driven, max 700 chars. No excessive emojis, value-first.
- Facebook: Conversational, warm, max 500 chars. Question-based engagement.
- TikTok: Punchy, trend-aware, max 150 chars. Very short, hook-first.
- YouTube Shorts: Descriptive, SEO-aware, max 100 chars. Keywords in first 40 chars.

RULES:
- Match the provided brand tone exactly.
- No two captions may share identical text.
- Each must be uniquely written for its platform.
- Include a CTA in every caption.

Return ONLY valid JSON:
{
  "captions": {
    "instagram": {"text": "...", "cta": "..."},
    "linkedin": {"text": "...", "cta": "..."},
    "facebook": {"text": "...", "cta": "..."},
    "tiktok": {"text": "...", "cta": "..."},
    "youtube_shorts": {"text": "...", "cta": "..."}
  }
}"""


class CaptionAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "captions_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        research = await self._resolve_research(payload)
        personas = await self._resolve_personas(payload)
        hooks = await self._resolve_hooks(payload)
        brand = await self._resolve_brand(payload)

        context = f"""RESEARCH:\n{json.dumps(research, indent=2)[:1500]}

PERSONAS:\n{json.dumps(personas, indent=2)[:1000]}

HOOKS (use as inspiration):\n{json.dumps(hooks, indent=2)[:1000]}

BRAND VOICE: {json.dumps(brand.get('tone', ['professional']))}
BRAND NAME: {brand.get('brand_name', 'the product')}"""

        provider = get_provider()
        captions = provider.generate_json(
            system=_CAPTION_SYSTEM,
            user=f"Generate platform-specific captions:\n\n{context}",
        )

        return {"captions": captions, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("captions", {}), "social media captions")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["captions"] = retry["captions"]
                validation = validate_content(result["captions"], "social media captions")
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
            content_type="caption",
            content_json=result.get("captions", {}),
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
            user_id=self.user_id, event=self.event_type, agent="caption_agent",
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
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "target_audience_summary": s.target_audience_summary}
        return {"product_name": payload.get("product_name", "")}

    async def _resolve_personas(self, payload: dict) -> dict:
        if "personas" in payload and isinstance(payload["personas"], dict):
            return payload["personas"]
        cid = payload.get("persona_content_id")
        if cid:
            r = await self.db.execute(select(CampaignContent).filter(CampaignContent.id == cid, CampaignContent.content_type == "persona"))
            c = r.scalars().first()
            if c:
                return c.content_json or {}
        return {}

    async def _resolve_hooks(self, payload: dict) -> dict:
        if "hooks" in payload and isinstance(payload["hooks"], dict):
            return payload["hooks"]
        cid = payload.get("hooks_content_id")
        if cid:
            r = await self.db.execute(select(CampaignContent).filter(CampaignContent.id == cid, CampaignContent.content_type == "hooks"))
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
                return {"brand_name": bp.brand_name, "tone": bp.tone or ["professional"]}
        # Try user's default
        r = await self.db.execute(select(BrandProfile).filter(BrandProfile.user_id == self.user_id, BrandProfile.is_default == 1))
        bp = r.scalars().first()
        if bp:
            return {"brand_name": bp.brand_name, "tone": bp.tone or ["professional"]}
        return {"brand_name": "the product", "tone": ["professional"]}
