"""
VideoProvider — abstract interface for video generation backends.

Implementations: KlingProvider (MVP), future RunwayProvider.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class VideoGenerationError(Exception):
    """Raised when video generation fails."""


class VideoProvider(ABC):

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier."""

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        *,
        duration_seconds: int = 5,
        aspect_ratio: str = "9:16",
        style: str = "realistic",
    ) -> dict[str, Any]:
        """
        Start video generation.
        Returns: {"job_id": str, "status": "processing", "provider": str}
        """

    @abstractmethod
    async def check_status(self, job_id: str) -> dict[str, Any]:
        """
        Check generation status.
        Returns: {"job_id": str, "status": "processing|completed|failed", "video_url": str|None}
        """

    @abstractmethod
    async def download_video(self, video_url: str, output_path: str) -> str:
        """
        Download generated video to local path.
        Returns the output_path on success.
        """
