from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all AutoMind Agents.
    Forces all agents to expose a standard orchestration interface.
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's core task."""
        pass

    @abstractmethod
    async def status(self, task_id: str) -> Dict[str, Any]:
        """Check the status of an ongoing agent task."""
        pass

    @abstractmethod
    async def history(self) -> list[Dict[str, Any]]:
        """Retrieve the agent's task history for this user."""
        pass
