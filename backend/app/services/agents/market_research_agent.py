"""
MarketResearchAgent — Sprint 3.1B (upgraded)

BEFORE (Sprint 3.1A): Website → Bedrock → ResearchSnapshot (pure LLM generation)
AFTER  (Sprint 3.1B): Website → MarketIntelligenceService → Bedrock Synthesis → ResearchSnapshot

The intelligence layer provides:
  - Website extraction (scraped data)
  - Trend intelligence (trending keywords, hashtags, content formats, CTA styles)
  - Competitor intelligence (positioning, strengths, weaknesses, messaging angles)

Bedrock is instructed to SYNTHESIZE the provided evidence — not invent information.

Generation model: Claude Sonnet (via settings.BEDROCK_MODEL_ID)
Validation model: Claude Haiku (via settings.BEDROCK_HAIKU_MODEL_ID)
Credit cost: 5 credits (unchanged — intelligence gathering is internal optimization)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.marketing import ResearchSnapshot, CampaignContent
from app.models.activity import ActivityEvent
from app.services.intelligence.market_intelligence_service import MarketIntelligenceService
from app.services.llm.provider_registry import get_provider
from app.core.config import settings
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_RESEARCH_SYSTEM = """You are a senior market research analyst specialising in digital marketing strategy.

IMPORTANT: You have been provided with real market intelligence data including:
- Website extraction (scraped content from the product's website)
- Trend intelligence (current trending keywords, hashtags, content formats in this industry)
- Competitor intelligence (competitive positioning, strengths, weaknesses, messaging angles)

Your job is to SYNTHESIZE this intelligence into a cohesive research report.
Do NOT invent trends, competitors, or data not provided in the intelligence context.
Ground every insight in the evidence supplied.

Return ONLY a valid JSON object with these exact keys:
{
  "company_summary": "<2-3 sentence overview synthesized from website data>",
  "market_position": "<positioning based on competitor intelligence>",
  "core_benefits": ["<benefit from website extraction>", ...],
  "competitor_summary": "<synthesized from competitor intelligence data>",
  "extracted_keywords": ["<from trend intelligence + website>", ...],
  "target_audience_summary": "<derived from trends + competitor gaps>",
  "trending_hooks": ["<top 3 trending angles from trend data>"],
  "content_opportunities": ["<gaps identified from competitor analysis>"]
}"""


class MarketResearchAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "market_research_completed"

    _payload: dict[str, Any] = {}
    _intelligence: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")
        website_url = payload.get("website_url", "")
        product_name = payload.get("product_name", "")
        product_description = payload.get("product_description", "")
        industry = payload.get("industry", "")

        # ── Step 1: Gather intelligence via MarketIntelligenceService ────────
        intel_service = MarketIntelligenceService(self.db)
        self._intelligence = await intel_service.get_intelligence(
            industry=industry or "general",
            website_url=website_url,
            product_name=product_name,
        )

        website_data = self._intelligence.get("website_data", {})
        trend_data = self._intelligence.get("trend_data", {})
        competitor_data = self._intelligence.get("competitor_data", {})

        # ── Step 2: Build evidence-backed LLM context ────────────────────────
        context = self._build_context(
            product_name=product_name,
            product_description=product_description,
            industry=industry,
            website_url=website_url,
            website_data=website_data,
            trend_data=trend_data,
            competitor_data=competitor_data,
        )

        # ── Step 3: Bedrock synthesis (not generation from scratch) ──────────
        provider = get_provider()
        research_data = provider.generate_json(
            system=_RESEARCH_SYSTEM,
            user=f"Synthesize the following market intelligence into a research report:\n\n{context}",
        )

        return {
            "research": research_data,
            "intelligence": self._intelligence,
            "scrape_data": website_data,
            "payload": payload,
        }

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        research = result.get("research", {})
        validation = validate_content(research, "market research report")

        if not validation["passed"]:
            logger.info(
                "MarketResearchAgent: quality score %d < 80, regenerating...",
                validation["quality_score"],
            )
            try:
                retry_result = await self.run(result["payload"])
                research = retry_result["research"]
                validation = validate_content(research, "market research report")
                result["research"] = research
            except Exception as exc:
                logger.warning("MarketResearchAgent: retry failed: %s", exc)

        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        payload = result["payload"]
        research = result["research"]
        website_data = result.get("scrape_data", {})
        validation = result.get("validation", {})

        # Persist ResearchSnapshot
        snapshot = ResearchSnapshot(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            website_url=payload.get("website_url"),
            product_name=payload.get("product_name"),
            industry=payload.get("industry"),
            company_summary=research.get("company_summary"),
            market_position=research.get("market_position"),
            core_benefits=research.get("core_benefits"),
            competitor_summary=research.get("competitor_summary"),
            extracted_keywords=research.get("extracted_keywords"),
            target_audience_summary=research.get("target_audience_summary"),
            scraped_title=website_data.get("title"),
            scraped_description=website_data.get("meta_description"),
            scraped_h1=website_data.get("h1"),
            scraped_main_text=website_data.get("main_text_snippet"),
        )
        self.db.add(snapshot)
        await self.db.flush()

        # Persist CampaignContent envelope
        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="research",
            content_json=research,
            quality_score=result.get("quality_score"),
            validation_json={
                "issues": validation.get("issues", []),
                "recommendations": validation.get("recommendations", []),
            },
            validation_passed=1 if validation.get("passed", False) else 0,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(snapshot)
        await self.db.refresh(content)

        result["snapshot_id"] = snapshot.id
        result["content_id"] = content.id
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        intelligence = result.get("intelligence", {})
        trend_cached = intelligence.get("trend_data", {}).get("cached", False)
        competitor_cached = intelligence.get("competitor_data", {}).get("cached", False)

        event = ActivityEvent(
            user_id=self.user_id,
            event=self.event_type,
            agent="market_research_agent",
            credits_used=self.credit_cost,
            job_id=job_id,
            campaign_id=self._campaign_id,
            metadata_json={
                "snapshot_id": result.get("snapshot_id"),
                "content_id": result.get("content_id"),
                "quality_score": result.get("quality_score"),
                "product_name": result["payload"].get("product_name"),
                "intelligence_source": "market_intelligence_service",
                "trend_cache_hit": trend_cached,
                "competitor_cache_hit": competitor_cached,
            },
        )
        self.db.add(event)
        await self.db.commit()

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _build_context(
        self,
        product_name: str,
        product_description: str,
        industry: str,
        website_url: str,
        website_data: dict[str, Any],
        trend_data: dict[str, Any],
        competitor_data: dict[str, Any],
    ) -> str:
        """Build the evidence-backed context string for Bedrock synthesis."""
        sections = []

        # Product info
        sections.append(f"""=== PRODUCT INFORMATION ===
Product Name: {product_name}
Product Description: {product_description}
Industry: {industry}
Website URL: {website_url}""")

        # Website extraction
        if website_data:
            sections.append(f"""=== WEBSITE EXTRACTION (Evidence) ===
Title: {website_data.get('title', 'N/A')}
Description: {website_data.get('meta_description', 'N/A')}
Main Content: {website_data.get('main_text_snippet', 'N/A')[:1500]}
Headings: {json.dumps(website_data.get('h1', [])[:5])}
CTAs Found: {json.dumps(website_data.get('extracted_ctas', [])[:5])}""")

        # Trend intelligence
        if trend_data and trend_data.get("keywords"):
            sections.append(f"""=== TREND INTELLIGENCE (Evidence) ===
Trending Keywords: {json.dumps(trend_data.get('keywords', [])[:10])}
Trending Hashtags: {json.dumps(trend_data.get('hashtags', [])[:10])}
Trending Content Formats: {json.dumps(trend_data.get('content_formats', [])[:5])}
Trending CTA Styles: {json.dumps(trend_data.get('cta_styles', [])[:5])}""")

        # Competitor intelligence
        competitors = competitor_data.get("competitors", [])
        if competitors:
            comp_summary = []
            for c in competitors[:5]:
                comp_summary.append(
                    f"- {c.get('competitor_name', 'Unknown')}: "
                    f"Position: {c.get('positioning', 'N/A')[:100]}. "
                    f"Strengths: {', '.join(c.get('strengths', [])[:3])}. "
                    f"Weaknesses: {', '.join(c.get('weaknesses', [])[:3])}."
                )
            sections.append(f"""=== COMPETITOR INTELLIGENCE (Evidence) ===
{chr(10).join(comp_summary)}
Messaging Angles: {json.dumps([a for c in competitors[:3] for a in c.get('messaging_angles', [])[:2]])}
Content Opportunities: {json.dumps([o for c in competitors[:3] for o in c.get('content_opportunities', [])[:2]])}""")

        return "\n\n".join(sections)
