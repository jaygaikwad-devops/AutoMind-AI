"""
PersonaAgent — Sprint 3.1A

Input:  snapshot_id (ResearchSnapshot) or raw research dict
Output: CampaignContent (content_type="persona") with 3–5 audience personas

Generation model: Claude Sonnet
Validation model: Claude Haiku
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

_PERSONA_SYSTEM = """You are a senior audience strategist and buyer psychology expert.
Based on the market research provided, create 3–5 detailed target customer personas.

Return ONLY a valid JSON object with this exact structure:
{
  "personas": [
    {
      "name": "<persona name>",
      "age_range": "<e.g. 28-35>",
      "job_title": "<typical job title>",
      "demographics": "<1-2 sentence description>",
      "pain_points": ["<pain 1>", "<pain 2>", "<pain 3>"],
      "motivations": ["<motivation 1>", "<motivation 2>"],
      "buying_triggers": ["<trigger 1>", "<trigger 2>"],
      "objections": ["<objection 1>", "<objection 2>"],
      "preferred_channels": ["<channel 1>", "<channel 2>"]
    }
  ]
}"""


class PersonaAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "persona_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        # Resolve research context — either from DB snapshot or inline dict
        research_context = await self._resolve_research(payload)

        provider = get_provider()
        personas_data = provider.generate_json(
            system=_PERSONA_SYSTEM,
            user=f"Generate audience personas based on this market research:\n\n{json.dumps(research_context, indent=2)[:3000]}",
        )

        return {
            "personas": personas_data,
            "research_context": research_context,
            "payload": payload,
        }

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        personas = result.get("personas", {})
        validation = validate_content(personas, "audience personas")

        if not validation["passed"]:
            logger.info(
                "PersonaAgent: quality score %d < 80, regenerating...",
                validation["quality_score"],
            )
            try:
                retry_result = await self.run(result["payload"])
                personas = retry_result["personas"]
                validation = validate_content(personas, "audience personas")
                result["personas"] = personas
            except Exception as exc:
                logger.warning("PersonaAgent: retry failed: %s", exc)

        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = result.get("validation", {})
        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="persona",
            content_json=result.get("personas", {}),
            quality_score=result.get("quality_score"),
            validation_json={
                "issues": validation.get("issues", []),
                "recommendations": validation.get("recommendations", []),
            },
            validation_passed=1 if validation.get("passed", False) else 0,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)

        result["content_id"] = content.id
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        personas = result.get("personas", {})
        count = len(personas.get("personas", [])) if isinstance(personas, dict) else 0
        event = ActivityEvent(
            user_id=self.user_id,
            event=self.event_type,
            agent="persona_agent",
            credits_used=self.credit_cost,
            job_id=job_id,
            campaign_id=self._campaign_id,
            metadata_json={
                "content_id": result.get("content_id"),
                "persona_count": count,
                "quality_score": result.get("quality_score"),
            },
        )
        self.db.add(event)
        await self.db.commit()

    # ------------------------------------------------------------------
    async def _resolve_research(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Return a research context dict either from:
        1. An inline 'research' key in payload, or
        2. A 'snapshot_id' FK into ResearchSnapshot, or
        3. A fallback minimal context from product fields.
        """
        # Inline research dict
        if "research" in payload and isinstance(payload["research"], dict):
            return payload["research"]

        # Load from ResearchSnapshot
        snapshot_id = payload.get("snapshot_id")
        if snapshot_id:
            result = await self.db.execute(
                select(ResearchSnapshot).filter(ResearchSnapshot.id == snapshot_id)
            )
            snapshot = result.scalars().first()
            if snapshot:
                return {
                    "company_summary": snapshot.company_summary,
                    "market_position": snapshot.market_position,
                    "core_benefits": snapshot.core_benefits,
                    "competitor_summary": snapshot.competitor_summary,
                    "extracted_keywords": snapshot.extracted_keywords,
                    "target_audience_summary": snapshot.target_audience_summary,
                    "product_name": snapshot.product_name,
                    "industry": snapshot.industry,
                }

        # Fallback — build minimal context from payload fields
        return {
            "product_name": payload.get("product_name", ""),
            "product_description": payload.get("product_description", ""),
            "industry": payload.get("industry", ""),
            "target_audience_summary": payload.get("target_audience", ""),
        }
