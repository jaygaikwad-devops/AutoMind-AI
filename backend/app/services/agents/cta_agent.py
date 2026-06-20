"""
CTAAgent — Sprint 3.1C

Generates categorized CTAs: Urgency, Scarcity, Authority, Curiosity, Offer.
Consumes: Persona, BrandProfile, Ad Copy output.
Persists: CampaignContent(content_type="cta")
Credit cost: 3
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.future import select

from app.models.marketing import CampaignContent, BrandProfile
from app.models.activity import ActivityEvent
from app.services.llm.provider_registry import get_provider
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_CTA_SYSTEM = """You are a conversion optimization specialist.
Generate CTAs using psychological triggers, tailored to the brand voice.

CATEGORIES:
- urgency: Time pressure, deadline-driven
- scarcity: Limited availability, exclusive access
- authority: Social proof, expert endorsement, credibility
- curiosity: Knowledge gap, mystery, intrigue
- offer: Value proposition, discount, free trial

Each CTA includes:
- text: The CTA copy
- context: Where it works best (landing_page, email, ad, popup, social, pricing_page)

Generate at least 2 CTAs per category (10+ total).
Match the provided brand tone exactly.

Return ONLY valid JSON:
{
  "ctas": {
    "urgency": [{"text": "...", "context": "..."}],
    "scarcity": [{"text": "...", "context": "..."}],
    "authority": [{"text": "...", "context": "..."}],
    "curiosity": [{"text": "...", "context": "..."}],
    "offer": [{"text": "...", "context": "..."}]
  },
  "total_ctas": 10
}"""


class CTAAgent(BaseAgent):

    credit_cost: int = 3
    event_type: str = "cta_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        personas = await self._resolve_personas(payload)
        adcopy = await self._resolve_adcopy(payload)
        brand = await self._resolve_brand(payload)

        context = f"""PERSONAS:\n{json.dumps(personas, indent=2)[:1000]}

AD COPY CONTEXT:\n{json.dumps(adcopy, indent=2)[:1000]}

BRAND VOICE: {json.dumps(brand.get('tone', ['professional']))}
BRAND NAME: {brand.get('brand_name', 'the product')}"""

        provider = get_provider()
        ctas = provider.generate_json(
            system=_CTA_SYSTEM,
            user=f"Generate categorized CTAs:\n\n{context}",
        )

        return {"ctas": ctas, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("ctas", {}), "calls to action")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["ctas"] = retry["ctas"]
                validation = validate_content(result["ctas"], "calls to action")
            except Exception:
                pass
        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = result.get("validation", {})
        ctas = result.get("ctas", {})
        total = sum(len(ctas.get(k, [])) for k in ("urgency", "scarcity", "authority", "curiosity", "offer")) if isinstance(ctas, dict) else 0

        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="cta",
            content_json=ctas,
            quality_score=result.get("quality_score"),
            validation_json={"issues": validation.get("issues", []), "recommendations": validation.get("recommendations", [])},
            validation_passed=1 if validation.get("passed") else 0,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        result["content_id"] = content.id
        result["total_ctas"] = total
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        event = ActivityEvent(
            user_id=self.user_id, event=self.event_type, agent="cta_agent",
            credits_used=self.credit_cost, job_id=job_id, campaign_id=self._campaign_id,
            metadata_json={"content_id": result.get("content_id"), "total_ctas": result.get("total_ctas"), "quality_score": result.get("quality_score")},
        )
        self.db.add(event)
        await self.db.commit()

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

    async def _resolve_adcopy(self, payload: dict) -> dict:
        if "adcopy" in payload and isinstance(payload["adcopy"], dict):
            return payload["adcopy"]
        cid = payload.get("adcopy_content_id")
        if cid:
            r = await self.db.execute(select(CampaignContent).filter(CampaignContent.id == cid, CampaignContent.content_type == "adcopy"))
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
        r = await self.db.execute(select(BrandProfile).filter(BrandProfile.user_id == self.user_id, BrandProfile.is_default == 1))
        bp = r.scalars().first()
        if bp:
            return {"brand_name": bp.brand_name, "tone": bp.tone or ["professional"]}
        return {"brand_name": "the product", "tone": ["professional"]}
