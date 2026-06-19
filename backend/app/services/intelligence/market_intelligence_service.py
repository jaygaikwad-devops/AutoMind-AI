"""
MarketIntelligenceService — Sprint 3.1B

Provides evidence-backed intelligence to all marketing agents.
Aggregates: website extraction + trend intelligence + competitor intelligence.

Cache strategy: PostgreSQL-based with 24-hour TTL via expires_at column.
No Redis. No external trend APIs (Sprint 3.2 will add those).

Usage:
    service = MarketIntelligenceService(db)
    intel = await service.get_intelligence(
        industry="saas",
        website_url="https://example.com",
        product_name="My Product",
    )
    # intel = {"website_data": {...}, "trend_data": {...}, "competitor_data": {...}}
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.trend_snapshot import TrendSnapshot
from app.models.competitor_snapshot import CompetitorSnapshot
from app.services.campaigns.analyzer import analyze_website
from app.services.llm.provider_registry import get_provider
from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Bedrock prompts ──────────────────────────────────────────────────────────

_TREND_SYSTEM = """You are a social media trend analyst and content strategist.
For the given industry, identify current trending signals across major platforms.

Return ONLY a valid JSON object with these exact keys:
{
  "keywords": ["<trending keyword 1>", "<trending keyword 2>", ...],
  "hashtags": ["#hashtag1", "#hashtag2", ...],
  "content_formats": ["<format 1>", "<format 2>", ...],
  "cta_styles": ["<cta style 1>", "<cta style 2>", ...],
  "confidence_score": <float 0.0-1.0>
}

Generate 10-15 items per category. Focus on what is trending RIGHT NOW in this industry.
Keywords: search terms people are actively using.
Hashtags: viral or high-engagement hashtags in this space.
Content formats: types of content performing well (e.g. "short-form video", "carousel", "listicle").
CTA styles: call-to-action approaches that are converting (e.g. "urgency", "social proof", "free trial")."""

_COMPETITOR_SYSTEM = """You are a competitive intelligence analyst specializing in digital marketing.
For the given industry and product context, identify the top 3-5 competitors and analyze each.

Return ONLY a valid JSON object with this exact structure:
{
  "competitors": [
    {
      "competitor_name": "<name>",
      "positioning": "<how they position themselves>",
      "strengths": ["<strength 1>", "<strength 2>"],
      "weaknesses": ["<weakness 1>", "<weakness 2>"],
      "messaging_angles": ["<angle 1>", "<angle 2>"],
      "content_opportunities": ["<opportunity 1>", "<opportunity 2>"],
      "keywords": ["<keyword 1>", "<keyword 2>"]
    }
  ],
  "confidence_score": <float 0.0-1.0>
}

Be specific. Name real companies when possible. Focus on digital marketing positioning."""


class MarketIntelligenceService:
    """
    Central intelligence aggregator for all marketing agents.
    Manages Bedrock-generated trend and competitor data with DB caching.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    async def get_intelligence(
        self,
        industry: str,
        website_url: str | None = None,
        product_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Returns combined intelligence dict:
        {
            "website_data": { ... },
            "trend_data": { ... },
            "competitor_data": { ... }
        }

        Each sub-dict is populated from cache or freshly generated.
        Failures in any component return empty dicts — never raises.
        """
        # Run all three intelligence streams concurrently
        website_task = self._get_website_data(website_url)
        trend_task = self._get_trend_data(industry)
        competitor_task = self._get_competitor_data(industry, product_name)

        website_data, trend_data, competitor_data = await asyncio.gather(
            website_task, trend_task, competitor_task,
            return_exceptions=True,
        )

        # Convert exceptions to empty dicts
        if isinstance(website_data, BaseException):
            logger.warning("Website extraction failed: %s", website_data)
            website_data = {}
        if isinstance(trend_data, BaseException):
            logger.warning("Trend intelligence failed: %s", trend_data)
            trend_data = {}
        if isinstance(competitor_data, BaseException):
            logger.warning("Competitor intelligence failed: %s", competitor_data)
            competitor_data = {}

        return {
            "website_data": website_data,
            "trend_data": trend_data,
            "competitor_data": competitor_data,
        }

    async def get_trends(self, industry: str) -> dict[str, Any]:
        """Get trend data only (for agents that only need trends)."""
        return await self._get_trend_data(industry)

    async def get_competitors(self, industry: str, product_name: str | None = None) -> dict[str, Any]:
        """Get competitor data only (for agents that only need competitive intel)."""
        return await self._get_competitor_data(industry, product_name)

    # ──────────────────────────────────────────────────────────────────────────
    # Website extraction
    # ──────────────────────────────────────────────────────────────────────────

    async def _get_website_data(self, website_url: str | None) -> dict[str, Any]:
        """Scrape website using existing analyzer. Returns empty dict on failure."""
        if not website_url:
            return {}
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, analyze_website, website_url)
            return data
        except Exception as exc:
            logger.warning("Website scrape failed for %s: %s", website_url, exc)
            return {}

    # ──────────────────────────────────────────────────────────────────────────
    # Trend intelligence (cached)
    # ──────────────────────────────────────────────────────────────────────────

    async def _get_trend_data(self, industry: str) -> dict[str, Any]:
        """Check cache → return valid trends or generate fresh ones."""
        industry_lower = industry.strip().lower() if industry else "general"
        now = datetime.utcnow()

        # Check cache
        result = await self.db.execute(
            select(TrendSnapshot)
            .filter(
                TrendSnapshot.industry == industry_lower,
                TrendSnapshot.expires_at > now,
            )
            .order_by(TrendSnapshot.captured_at.desc())
            .limit(1)
        )
        cached = result.scalars().first()

        if cached:
            logger.info("TrendSnapshot cache HIT for industry=%s", industry_lower)
            return {
                "snapshot_id": cached.id,
                "industry": cached.industry,
                "platform": cached.platform,
                "keywords": cached.keywords_json or [],
                "hashtags": cached.hashtags_json or [],
                "content_formats": cached.content_formats_json or [],
                "cta_styles": cached.cta_styles_json or [],
                "confidence_score": cached.confidence_score,
                "cached": True,
            }

        # Cache miss — generate via Bedrock
        logger.info("TrendSnapshot cache MISS for industry=%s — generating", industry_lower)
        return await self._generate_trends(industry_lower)

    async def _generate_trends(self, industry: str) -> dict[str, Any]:
        """Generate trend data via Bedrock and persist TrendSnapshot."""
        provider = get_provider()
        try:
            data = provider.generate_json(
                system=_TREND_SYSTEM,
                user=f"Generate current trending signals for the {industry} industry across Instagram, TikTok, LinkedIn, and YouTube.",
            )
        except Exception as exc:
            logger.error("Trend generation via Bedrock failed: %s", exc)
            return {}

        # Persist
        snapshot = TrendSnapshot(
            industry=industry,
            platform="multi",  # covers multiple platforms in one snapshot
            keywords_json=data.get("keywords", []),
            hashtags_json=data.get("hashtags", []),
            content_formats_json=data.get("content_formats", []),
            cta_styles_json=data.get("cta_styles", []),
            confidence_score=data.get("confidence_score", 0.7),
        )
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)

        return {
            "snapshot_id": snapshot.id,
            "industry": snapshot.industry,
            "platform": snapshot.platform,
            "keywords": snapshot.keywords_json or [],
            "hashtags": snapshot.hashtags_json or [],
            "content_formats": snapshot.content_formats_json or [],
            "cta_styles": snapshot.cta_styles_json or [],
            "confidence_score": snapshot.confidence_score,
            "cached": False,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Competitor intelligence (cached)
    # ──────────────────────────────────────────────────────────────────────────

    async def _get_competitor_data(self, industry: str, product_name: str | None = None) -> dict[str, Any]:
        """Check cache → return valid competitors or generate fresh ones."""
        industry_lower = industry.strip().lower() if industry else "general"
        now = datetime.utcnow()

        # Check cache — get all non-expired competitors for this industry
        result = await self.db.execute(
            select(CompetitorSnapshot)
            .filter(
                CompetitorSnapshot.industry == industry_lower,
                CompetitorSnapshot.expires_at > now,
            )
            .order_by(CompetitorSnapshot.created_at.desc())
        )
        cached_list = result.scalars().all()

        if cached_list:
            logger.info(
                "CompetitorSnapshot cache HIT for industry=%s (%d competitors)",
                industry_lower, len(cached_list),
            )
            competitors = []
            for c in cached_list:
                competitors.append({
                    "competitor_name": c.competitor_name,
                    "positioning": c.positioning,
                    "strengths": c.strengths_json or [],
                    "weaknesses": c.weaknesses_json or [],
                    "messaging_angles": c.messaging_angles_json or [],
                    "content_opportunities": c.content_opportunities_json or [],
                    "keywords": c.keywords_json or [],
                })
            return {
                "industry": industry_lower,
                "competitors": competitors,
                "cached": True,
            }

        # Cache miss — generate via Bedrock
        logger.info("CompetitorSnapshot cache MISS for industry=%s — generating", industry_lower)
        return await self._generate_competitors(industry_lower, product_name)

    async def _generate_competitors(self, industry: str, product_name: str | None) -> dict[str, Any]:
        """Generate competitor data via Bedrock and persist CompetitorSnapshots."""
        provider = get_provider()
        context = f"Industry: {industry}"
        if product_name:
            context += f"\nProduct: {product_name}"

        try:
            data = provider.generate_json(
                system=_COMPETITOR_SYSTEM,
                user=f"Analyze the competitive landscape:\n\n{context}",
            )
        except Exception as exc:
            logger.error("Competitor generation via Bedrock failed: %s", exc)
            return {"industry": industry, "competitors": [], "cached": False}

        competitors_raw = data.get("competitors", [])
        confidence = data.get("confidence_score", 0.7)

        # Persist each competitor as a separate row
        persisted = []
        for comp in competitors_raw:
            snapshot = CompetitorSnapshot(
                industry=industry,
                competitor_name=comp.get("competitor_name", "Unknown"),
                positioning=comp.get("positioning"),
                strengths_json=comp.get("strengths", []),
                weaknesses_json=comp.get("weaknesses", []),
                messaging_angles_json=comp.get("messaging_angles", []),
                content_opportunities_json=comp.get("content_opportunities", []),
                keywords_json=comp.get("keywords", []),
                confidence_score=confidence,
            )
            self.db.add(snapshot)
            persisted.append(comp)

        await self.db.commit()

        return {
            "industry": industry,
            "competitors": persisted,
            "cached": False,
        }
