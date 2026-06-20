"""
ListingAgent — MVP Launch

Generates marketplace listings for Amazon and Flipkart.
User manually copies output into the marketplace — NO API integration.

Consumes: ResearchSnapshot, product info.
Persists: CampaignContent(content_type="amazon_listing" or "flipkart_listing")
Credit cost: 5
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.future import select

from app.models.marketing import ResearchSnapshot, CampaignContent
from app.models.activity import ActivityEvent
from app.services.llm.provider_registry import get_provider
from .base import BaseAgent
from .validation import validate_content

logger = logging.getLogger(__name__)

_AMAZON_SYSTEM = """You are an Amazon listing optimization expert.
Generate a fully optimized Amazon product listing.

Return ONLY valid JSON:
{
  "title": "<max 200 chars, keyword-rich product title>",
  "bullet_points": [
    "<bullet 1 — lead with benefit, include keyword>",
    "<bullet 2>",
    "<bullet 3>",
    "<bullet 4>",
    "<bullet 5>"
  ],
  "description": "<500-1000 chars, compelling product description with keywords>",
  "search_keywords": ["<backend keyword 1>", "<keyword 2>", "<keyword 3>", ...]
}

RULES:
- Title: Brand + Key Feature + Product Type + Size/Color. Max 200 chars.
- Bullet points: Start with CAPS benefit, then explain. Max 500 chars each.
- Description: Storytelling + features + benefits. Include relevant keywords.
- Keywords: 5-10 backend search terms not already in title."""

_FLIPKART_SYSTEM = """You are a Flipkart listing optimization expert.
Generate a fully optimized Flipkart product listing.

Return ONLY valid JSON:
{
  "title": "<max 100 chars, clear product title>",
  "description": "<500-800 chars, clear product description>",
  "key_features": [
    "<feature 1>",
    "<feature 2>",
    "<feature 3>",
    "<feature 4>",
    "<feature 5>",
    "<feature 6>"
  ],
  "search_keywords": ["<keyword 1>", "<keyword 2>", ...]
}

RULES:
- Title: Brand + Product + Key Spec. Max 100 chars.
- Description: Benefits-first, then technical specs.
- Key Features: 6 bullet points, concise and clear.
- Keywords: Terms buyers search on Flipkart."""


class AmazonListingAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "amazon_listing_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        research = await self._resolve_research(payload)
        product_name = payload.get("product_name", "")
        product_description = payload.get("product_description", "")

        context = f"""Product: {product_name}
Description: {product_description}
Research: {json.dumps(research, indent=2)[:1500]}"""

        provider = get_provider()
        listing = provider.generate_json(
            system=_AMAZON_SYSTEM,
            user=f"Generate an optimized Amazon listing:\n\n{context}",
        )

        return {"listing": listing, "marketplace": "amazon", "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("listing", {}), "Amazon product listing")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["listing"] = retry["listing"]
                validation = validate_content(result["listing"], "Amazon product listing")
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
            content_type="amazon_listing",
            content_json=result.get("listing", {}),
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
            user_id=self.user_id, event=self.event_type, agent="amazon_listing_agent",
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
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "product_name": s.product_name}
        return {"product_name": payload.get("product_name", "")}


class FlipkartListingAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "flipkart_listing_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        research = await self._resolve_research(payload)
        product_name = payload.get("product_name", "")
        product_description = payload.get("product_description", "")

        context = f"""Product: {product_name}
Description: {product_description}
Research: {json.dumps(research, indent=2)[:1500]}"""

        provider = get_provider()
        listing = provider.generate_json(
            system=_FLIPKART_SYSTEM,
            user=f"Generate an optimized Flipkart listing:\n\n{context}",
        )

        return {"listing": listing, "marketplace": "flipkart", "payload": payload}

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = validate_content(result.get("listing", {}), "Flipkart product listing")
        if not validation["passed"]:
            try:
                retry = await self.run(result["payload"])
                result["listing"] = retry["listing"]
                validation = validate_content(result["listing"], "Flipkart product listing")
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
            content_type="flipkart_listing",
            content_json=result.get("listing", {}),
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
            user_id=self.user_id, event=self.event_type, agent="flipkart_listing_agent",
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
                return {"company_summary": s.company_summary, "core_benefits": s.core_benefits, "extracted_keywords": s.extracted_keywords, "product_name": s.product_name}
        return {"product_name": payload.get("product_name", "")}
