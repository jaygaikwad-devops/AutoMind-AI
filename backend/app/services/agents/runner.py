"""
AgentRunner — orchestrates the full agent execution lifecycle.

Lifecycle (async, FastAPI context):
  1. Reserve credits
  2. Create CampaignJob (status=reserved)
  3. Set job status=running
  4. agent.run(payload)
  5. agent.validate(result)
  6. agent.persist(result)
  7. agent.emit_event(result, job_id)
  8. Commit credits + set job status=completed

On any exception after step 1:
  - Refund credits
  - Set job status=failed (with error_message)
  - Emit failure ActivityEvent
  - Re-raise so the router returns 500

On CreditReservationError (step 1):
  - Raise immediately as HTTP 402 — no job created
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.constants import JOB_STATUS
from app.models import User
from app.models.campaign import CampaignJob
from app.models.activity import ActivityEvent
from app.services.billing.credit_service import CreditService, CreditReservationError
from .base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRunner:
    """
    Usage::

        runner = AgentRunner(db, user_id)
        result = await runner.execute(agent, payload, campaign_id=campaign_id)
    """

    def __init__(self, db: AsyncSession, user_id: str) -> None:
        self.db = db
        self.user_id = user_id

    async def execute(
        self,
        agent: BaseAgent,
        payload: dict[str, Any],
        *,
        campaign_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run the agent through the complete lifecycle.
        Returns the fully-enriched result dict from persist().
        Raises CreditReservationError (402) or RuntimeError (500).
        """
        cost = agent.credit_cost
        job_id = str(uuid.uuid4())

        # ── Step 1: Reserve credits ──────────────────────────────────
        await CreditService.reserve_credits(self.db, self.user_id, cost, job_id)
        # From here, credits are reserved — refund on any failure.

        # ── Step 2: Create CampaignJob ───────────────────────────────
        job = CampaignJob(
            id=job_id,
            user_id=self.user_id,
            campaign_id=campaign_id,
            job_type=agent.event_type,
            status=JOB_STATUS["RESERVED"],
            credits_reserved=cost,
        )
        self.db.add(job)
        await self.db.commit()

        try:
            # ── Step 3: Mark running ─────────────────────────────────
            job.status = JOB_STATUS["RUNNING"]
            job.started_at = datetime.utcnow()
            await self.db.commit()

            # ── Step 4: Generate ─────────────────────────────────────
            result = await agent.run(payload)

            # ── Step 5: Validate ─────────────────────────────────────
            result = await agent.validate(result)

            # ── Step 6: Persist ──────────────────────────────────────
            result = await agent.persist(result)

            # ── Step 7: Emit success event ───────────────────────────
            await agent.emit_event(result, job_id)

            # ── Step 8: Commit credits + complete job ─────────────────
            actual_cost = result.get("credits_used", cost)
            await CreditService.commit_credits(self.db, self.user_id, actual_cost)
            job.status = JOB_STATUS["COMPLETED"]
            job.completed_at = datetime.utcnow()
            await self.db.commit()

            result["job_id"] = job_id
            result["credits_committed"] = actual_cost
            return result

        except Exception as exc:
            logger.error(
                "AgentRunner: agent %s failed for user %s job %s: %s",
                agent.event_type, self.user_id, job_id, exc,
            )
            # Refund + mark failed
            try:
                await CreditService.refund_credits(self.db, self.user_id, cost)
                job.status = JOB_STATUS["FAILED"]
                job.error_message = str(exc)
                job.completed_at = datetime.utcnow()
                # Emit failure event
                fail_event = ActivityEvent(
                    user_id=self.user_id,
                    event=f"{agent.event_type}_failed",
                    agent=agent.event_type,
                    credits_used=0,
                    job_id=job_id,
                    campaign_id=campaign_id,
                    metadata_json={"error": str(exc)},
                )
                self.db.add(fail_event)
                await self.db.commit()
            except Exception as cleanup_exc:
                logger.error("AgentRunner: cleanup after failure also failed: %s", cleanup_exc)
            raise
