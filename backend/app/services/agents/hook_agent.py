"""
HookAgent — Sprint 3.1A

Input:  snapshot_id + content_id (personas) or inline research/personas
Output: CampaignContent (content_type="hooks") with 40 hooks across 4 types:
        Curiosity (10), Pain (10), Emotional (10), Authority (10)

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

_HOOK_SYSTEM = """You are a world-class direct-response copywriter and viral content strategist.
Generate marketing hooks that are thumb-stopping, emotionally resonant, and drive action.

Based on the research and personas provided, write exactly 40 hooks — 10 per category.

Return ONLY a valid JSON object with this exact structure:
{
  "curiosity_hooks": [
    {"hook": "<hook text>", "score": <1-100>}
  ],
  "pain_hooks": [
    {"hook": "<hook text>", "score": <1-100>}
  ],
  "emotional_hooks": [
    {"hook": "<hook text>", "score": <1-100>}
  ],
  "authority_hooks": [
    {"hook": "<hook text>", "score": <1-100>}
  ]
}

Score represents predicted virality/effectiveness (1=weak, 100=exceptional).
Curiosity hooks: create knowledge gaps, tease surprising information.
Pain hooks: address specific frustrations, amplify the problem.
Emotional hooks: trigger aspiration, fear of missing out, or belonging.
Authority hooks: lead with credibility, results, or social proof."""


class HookAgent(BaseAgent):

    credit_cost: int = 5
    event_type: str = "hooks_generated"

    _payload: dict[str, Any] = {}
    _campaign_id: str | None = None

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._payload = payload
        self._campaign_id = payload.get("campaign_id")

        research_context = await self._resolve_research(payload)
        persona_context = await self._resolve_personas(payload)

        context_str = (
            f"MARKET RESEARCH:\n{json.dumps(research_context, indent=2)[:2000]}\n\n"
            f"AUDIENCE PERSONAS:\n{json.dumps(persona_context, indent=2)[:2000]}"
        )

        provider = get_provider()
        hooks_data = provider.generate_json(
            system=_HOOK_SYSTEM,
            user=f"Generate 40 marketing hooks for this product:\n\n{context_str}",
        )

        return {
            "hooks": hooks_data,
            "payload": payload,
        }

    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        hooks = result.get("hooks", {})
        # Validate a sample — first 5 hooks of each type
        sample = {}
        for hook_type in ("curiosity_hooks", "pain_hooks", "emotional_hooks", "authority_hooks"):
            sample[hook_type] = hooks.get(hook_type, [])[:5]

        validation = validate_content(sample, "marketing hooks")

        if not validation["passed"]:
            logger.info(
                "HookAgent: quality score %d < 80, regenerating...",
                validation["quality_score"],
            )
            try:
                retry_result = await self.run(result["payload"])
                hooks = retry_result["hooks"]
                validation = validate_content(hooks, "marketing hooks")
                result["hooks"] = hooks
            except Exception as exc:
                logger.warning("HookAgent: retry failed: %s", exc)

        result["quality_score"] = validation["quality_score"]
        result["validation"] = validation
        return result

    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        validation = result.get("validation", {})
        hooks = result.get("hooks", {})

        # Count total hooks
        total = sum(
            len(hooks.get(k, []))
            for k in ("curiosity_hooks", "pain_hooks", "emotional_hooks", "authority_hooks")
        )

        content = CampaignContent(
            user_id=self.user_id,
            campaign_id=self._campaign_id,
            content_type="hooks",
            content_json=hooks,
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
        result["total_hooks"] = total
        return result

    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        event = ActivityEvent(
            user_id=self.user_id,
            event=self.event_type,
            agent="hook_agent",
            credits_used=self.credit_cost,
            job_id=job_id,
            campaign_id=self._campaign_id,
            metadata_json={
                "content_id": result.get("content_id"),
                "total_hooks": result.get("total_hooks"),
                "quality_score": result.get("quality_score"),
            },
        )
        self.db.add(event)
        await self.db.commit()

    # ------------------------------------------------------------------
    async def _resolve_research(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "research" in payload and isinstance(payload["research"], dict):
            return payload["research"]
        snapshot_id = payload.get("snapshot_id")
        if snapshot_id:
            r = await self.db.execute(
                select(ResearchSnapshot).filter(ResearchSnapshot.id == snapshot_id)
            )
            snap = r.scalars().first()
            if snap:
                return {
                    "company_summary": snap.company_summary,
                    "core_benefits": snap.core_benefits,
                    "competitor_summary": snap.competitor_summary,
                    "extracted_keywords": snap.extracted_keywords,
                    "target_audience_summary": snap.target_audience_summary,
                    "product_name": snap.product_name,
                    "industry": snap.industry,
                }
        return {
            "product_name": payload.get("product_name", ""),
            "product_description": payload.get("product_description", ""),
        }

    async def _resolve_personas(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "personas" in payload and isinstance(payload["personas"], dict):
            return payload["personas"]
        content_id = payload.get("persona_content_id")
        if content_id:
            r = await self.db.execute(
                select(CampaignContent).filter(
                    CampaignContent.id == content_id,
                    CampaignContent.content_type == "persona",
                )
            )
            cc = r.scalars().first()
            if cc:
                return cc.content_json or {}
        return {}
