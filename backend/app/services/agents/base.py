"""
BaseAgent — abstract contract for all AutoMind agents.

Every concrete agent must implement:
  run()        — core generation logic
  validate()   — quality-check the output (may call Haiku)
  persist()    — write results to DB
  emit_event() — write ActivityEvent + return EventEnvelope dict

AgentRunner calls these in the correct lifecycle order and handles
credit reservation, commit, and refund.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):

    def __init__(self, db: AsyncSession, user_id: str) -> None:
        self.db = db
        self.user_id = user_id

    # ------------------------------------------------------------------
    # Required lifecycle methods (called by AgentRunner)
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent's core generation logic.
        Returns a result dict that is passed to validate() and persist().
        """

    @abstractmethod
    async def validate(self, result: dict[str, Any]) -> dict[str, Any]:
        """
        Quality-check the output (e.g. using Claude Haiku).
        Returns the result dict, optionally enriched with
        'quality_score', 'validation_issues', 'validation_recommendations'.
        Implementations may re-run run() once if score < 80.
        """

    @abstractmethod
    async def persist(self, result: dict[str, Any]) -> dict[str, Any]:
        """
        Persist validated output to the database.
        Returns the result dict enriched with database IDs.
        """

    @abstractmethod
    async def emit_event(self, result: dict[str, Any], job_id: str) -> None:
        """
        Write an ActivityEvent row for the completed job.
        """

    # ------------------------------------------------------------------
    # Optional helpers (legacy support — not called by AgentRunner)
    # ------------------------------------------------------------------

    async def status(self, task_id: str) -> dict[str, Any]:
        return {"task_id": task_id, "status": "unknown"}

    async def history(self) -> list[dict[str, Any]]:
        return []

    # ------------------------------------------------------------------
    # Credit cost — subclasses override
    # ------------------------------------------------------------------

    @property
    def credit_cost(self) -> int:
        """Override in subclass. Default 5 credits."""
        return 5

    @property
    def event_type(self) -> str:
        """Override in subclass. The event_type string for ActivityEvent.event."""
        return "agent_completed"
