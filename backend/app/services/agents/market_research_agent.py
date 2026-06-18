"""
MarketResearchAgent — Sprint 3.1A

Input:  website_url, product_name, product_description, industry
Output: ResearchSnapshot persisted to DB + CampaignContent (type=research)

Generation model: Claude Sonnet (via settings.BEDROCK_MODEL_ID)
Validation model: Claude Haiku (via settings.BEDROCK_HAIKU_MODEL_ID)
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
from app.services.campaigns.analyzer import analyze_website
from app.services.llm.provider_registry import get_provider
from app.core.config import settings
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_RESEARCH_SYSTEM = """You are a senior market research analyst specialising in digital marketing strategy.
Given a product and its website context, produce a comprehensive market research report.

Return ONLY a valid JSON object with these exact keys:
{
  "company_summary": "<2-3 sentence company overview>",
  "market_position": "<how this product is positioned in the market>",
  "core_benefits": ["<benefit 1>", "<benefit 2>", "<benefit 3>", ...],
  "competitor_summary": "<overview of main competitors and competitive landscape>",
  "extracted_keywords": ["<keyword 1>", "<keyword 2>", ...],
  "target_audience_summary": "<description of the ideal target audience>"
}"""


class MarketResearchAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "market_research_completed"

    # Store payload fields for use across lifecycle methods
    _payload: dict[str, Any] = {}
    _scrape_data: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")
        website_url = payload.get("website_url", "")
        product_name = payload.get("product_name", "")
        product_description = payload.get("product_description", "")
        industry = payload.get("industry", "")

        # Step 1: Scrape website
        self._scrape_data = {}
        if website_url:
            try:
                # analyze_website is sync — safe to call directly in async context
                # for small payloads; will be moved to run_in_executor in Sprint 3.2
                import asyncio
                loop = asyncio.get_event_loop()
                self._scrape_data = await loop.run_in_executor(
                    None, analyze_website, website_url
                )
            except Exception as exc:
                logger.warning("MarketResearchAgent: website scrape failed: %s", exc)

        # Step 2: Build LLM context
        context = f"""Product Name: {product_name}
Product Description: {product_description}
Industry: {industry}
Website URL: {website_url}

Website Content (scraped):
Title: {self._scrape_data.get('title', 'N/A')}
Description: {self._scrape_data.get('meta_description', 'N/A')}
Main Text: {self._scrape_data.get('main_text_snippet', 'N/A')[:2000]}
Headings: {json.dumps(self._scrape_data.get('h1', [])[:5])}"""

        # Step 3: Generate with Claude Sonnet
        provider = get_provider()
        research_data = provider.generate_json(
            system=_RESEARCH_SYSTEM,
            user=f"Produce market research for this product:\n\n{context}",
        )

        return {
            "research": research_data,
            "scrape_data": self._scrape_data,
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
            # One retry
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
        scrape = result.get("scrape_data", {})
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
            scraped_title=scrape.get("title"),
            scraped_description=scrape.get("meta_description"),
            scraped_h1=scrape.get("h1"),
            scraped_main_text=scrape.get("main_text_snippet"),
        )
        self.db.add(snapshot)
        await self.db.flush()  # get snapshot.id before CampaignContent

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
            },
        )
        self.db.add(event)
        await self.db.commit()
