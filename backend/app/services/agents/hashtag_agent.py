"""
HashtagAgent — Sprint 3.1C

Generates categorized hashtags (viral, niche, brand) with relevance and trend scores.
Consumes: TrendSnapshot, ResearchSnapshot, platform.
Persists: CampaignContent(content_type="hashtags")
Credit cost: 3
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

_HASHTAG_SYSTEM = """You are a hashtag strategist and social media growth expert.
Generate hashtags in three categories.

CATEGORIES:
- viral: High trend_score (60+), broad reach, currently trending
- niche: High relevance_score (80+), targeted audience, lower competition
- brand: Product-specific, company-related, high relevance

SCORING:
- relevance_score (0-100): How relevant is this hashtag to the product/industry?
- trend_score (0-100): How much is this hashtag trending right now?

Generate at least 5 hashtags per category (15+ total).

Return ONLY valid JSON:
{
  "viral_hashtags": [{"hashtag": "#...", "relevance_score": 85, "trend_score": 92}],
  "niche_hashtags": [{"hashtag": "#...", "relevance_score": 95, "trend_score": 40}],
  "brand_hashtags": [{"hashtag": "#...", "relevance_score": 100, "trend_score": 20}],
  "platform": "<platform>",
  "total_hashtags": 15
}"""


class HashtagAgent(BaseAgent):

    credit_cost: int = 3
    event_type: str = "hashtags_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")
        platform = payload.get("platform", "instagram")
        industry = payload.get("industry", "general")

        research = await self._resolve_research(payload)

        # Get trend data from intelligence service
        intel_service = MarketIntelligenceService(self.db)
        trend_data = await intel_service.get_trends(industry)

        context = f"""RESEARCH:\n{json.dumps(research, indent=2)[:1500]}

TRENDING DATA:\nKeywords: {json.dumps(trend_data.get('keywords', [])[:10])}
Hashtags: {json.dumps(trend_data.get('hashtags', [])[:10])}

TARGET PLATFORM: {platform}
INDUSTRY: {industry}"""

        provider = get_provider()
        hashtags = provider.generate_json(
            system=_HASHTAG_SYSTEM,
            user=f"Generate hashtags for {platform}:\n\n{context}",
        )

        return {"hashtags": hashtags, "platform": platform, "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("hashtags", {}), "hashtag strategy")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["hashtags"] = retry["hashtags"]
                validation = validate_content(result["hashtags"], "hashtag strategy")
            except Exception:
                pass
        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = result.get("validation", {})
        hashtags = result.get("hashtags", {})
        total = sum(len(hashtags.get(k, [])) for k in ("viral_hashtags", "niche_hashtags", "brand_hashtags"))

        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="hashtags",
            content_json=hashtags,
            quality_score=result.get("quality_score"),
            validation_json={"issues": validation.get("issues", []), "recommendations": validation.get("recommendations", [])},
            validation_passed=1 if validation.get("passed") else 0,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        result["content_id"] = content.id
        result["total_hashtags"] = total
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        event = ActivityEvent(
            user_id=self.user_id, event=self.event_type, agent="hashtag_agent",
            credits_used=self.credit_cost, job_id=job_id, campaign_id=self._campaign_id,
            metadata_json={"content_id": result.get("content_id"), "total_hashtags": result.get("total_hashtags"), "quality_score": result.get("quality_score")},
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
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "product_name": s.product_name, "industry": s.industry}
        return {"product_name": payload.get("product_name", "")}
