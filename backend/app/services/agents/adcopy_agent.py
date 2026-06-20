"""
AdCopyAgent — Sprint 3.1C

Generates ad copy using 5 frameworks: PAS, AIDA, Problem-Aware, Solution-Aware, Offer-Focused.
Consumes: ResearchSnapshot, Personas, Hooks, CompetitorSnapshot.
Persists: CampaignContent(content_type="adcopy")
Credit cost: 8
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.future import select

from app.models.marketing import ResearchSnapshot, CampaignContent
from app.models.activity import ActivityEvent
from app.services.intelligence.market_intelligence_service import MarketIntelligenceService
from app.services.llm.provider_registry import get_provider
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_ADCOPY_SYSTEM = """You are a direct-response advertising copywriter.
Generate ad copy using 5 proven frameworks. Use competitor weaknesses as leverage.

FRAMEWORKS:
1. PAS (Problem-Agitate-Solution): Lead with pain, amplify, offer solution
2. AIDA (Attention-Interest-Desire-Action): Classic attention funnel
3. Problem-Aware: For audience that knows the problem but not the solution
4. Solution-Aware: For audience that knows solutions exist but hasn't chosen
5. Offer-Focused: Lead with the value proposition and specific offer

AD SPECS (Meta/Google compatible):
- headline: max 40 characters
- primary_text: max 125 characters
- description: max 90 characters

Return ONLY valid JSON:
{
  "frameworks": {
    "pas": {"headline": "...", "primary_text": "...", "description": "..."},
    "aida": {"headline": "...", "primary_text": "...", "description": "..."},
    "problem_aware": {"headline": "...", "primary_text": "...", "description": "..."},
    "solution_aware": {"headline": "...", "primary_text": "...", "description": "..."},
    "offer_focused": {"headline": "...", "primary_text": "...", "description": "..."}
  }
}"""


class AdCopyAgent(BaseAgent):

    credit_cost: int = 8
    event_type: str = "adcopy_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")
        industry = payload.get("industry", "general")

        research = await self._resolve_research(payload)
        personas = await self._resolve_personas(payload)
        hooks = await self._resolve_hooks(payload)

        # Get competitor data
        intel_service = MarketIntelligenceService(self.db)
        competitor_data = await intel_service.get_competitors(industry)

        context = f"""RESEARCH:\n{json.dumps(research, indent=2)[:1500]}

PERSONAS:\n{json.dumps(personas, indent=2)[:800]}

HOOKS (use best ones as inspiration):\n{json.dumps(hooks, indent=2)[:800]}

COMPETITOR WEAKNESSES TO EXPLOIT:\n{json.dumps(competitor_data.get('competitors', [])[:3], indent=2)[:1000]}"""

        provider = get_provider()
        adcopy = provider.generate_json(
            system=_ADCOPY_SYSTEM,
            user=f"Generate ad copy using all 5 frameworks:\n\n{context}",
        )

        return {"adcopy": adcopy, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("adcopy", {}), "advertising copy")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["adcopy"] = retry["adcopy"]
                validation = validate_content(result["adcopy"], "advertising copy")
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
            content_type="adcopy",
            content_json=result.get("adcopy", {}),
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
            user_id=self.user_id, event=self.event_type, agent="adcopy_agent",
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
