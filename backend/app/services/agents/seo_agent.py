"""
SEOAgent — Sprint 3.1C (Lightweight for launch)

Generates: SEO Title, Meta Description, Outline, Keywords.
NO full blog draft for launch — just the SEO package.
Consumes: ResearchSnapshot, TrendSnapshot, CompetitorSnapshot.
Persists: CampaignContent(content_type="seo")
Credit cost: 5 (reduced from 10 since no blog draft)
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

_SEO_SYSTEM = """You are an SEO content strategist.
Generate an SEO content package based on the research and trending data.

OUTPUT:
- SEO Title: max 60 chars, includes primary keyword
- Meta Description: max 160 chars, compelling with primary keyword
- Outline: 5+ sections with subheadings for a future blog post
- Keywords: primary (1), secondary (3-5), long_tail (2-3)

Use trending keywords naturally. Reference competitor gaps as opportunities.

Return ONLY valid JSON:
{
  "seo_title": "...",
  "meta_description": "...",
  "outline": [{"heading": "...", "subheadings": ["..."]}],
  "keywords": {"primary": "...", "secondary": [...], "long_tail": [...]}
}"""


class SEOAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "seo_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")
        industry = payload.get("industry", "general")

        research = await self._resolve_research(payload)

        # Get trends + competitors
        intel_service = MarketIntelligenceService(self.db)
        trend_data = await intel_service.get_trends(industry)
        competitor_data = await intel_service.get_competitors(industry)

        context = f"""RESEARCH:\n{json.dumps(research, indent=2)[:1500]}

TRENDING KEYWORDS: {json.dumps(trend_data.get('keywords', [])[:10])}

COMPETITOR CONTENT GAPS:\n{json.dumps([c.get('content_opportunities', []) for c in competitor_data.get('competitors', [])[:3]], indent=2)[:800]}"""

        provider = get_provider()
        seo = provider.generate_json(
            system=_SEO_SYSTEM,
            user=f"Generate SEO content package:\n\n{context}",
        )

        return {"seo": seo, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("seo", {}), "SEO content package")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["seo"] = retry["seo"]
                validation = validate_content(result["seo"], "SEO content package")
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
            content_type="seo",
            content_json=result.get("seo", {}),
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
            user_id=self.user_id, event=self.event_type, agent="seo_agent",
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
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "target_audience_summary": s.target_audience_summary, "product_name": s.product_name, "industry": s.industry}
        return {"product_name": payload.get("product_name", "")}
