"""
KlingProvider — Kling AI video generation integration.

Workflow: Submit prompt → poll status → download MP4 → upload to S3.

Configuration via environment:
  KLING_API_KEY — API key for Kling
  KLING_API_BASE — Base URL (default: https://api.klingai.com)

This is a stub-ready implementation. When KLING_API_KEY is empty,
generate_video returns a placeholder response for testing.
"""
from __future__ import annotations

import logging
import os
import time
import httpx
from typing import Any

from app.core.config import settings
from .base import VideoProvider, VideoGenerationError

logger = logging.getLogger(__name__)

KLING_API_BASE = "https://api.klingai.com"


class KlingProvider(VideoProvider):

    def __init__(self) -> None:
        self._api_key = getattr(settings, "KLING_API_KEY", "")
        self._base_url = getattr(settings, "KLING_API_BASE", KLING_API_BASE)

    @property
    def provider_id(self) -> str:
        return "kling"

    async def generate_video(
        self,
        prompt: str,
        *,
        duration_seconds: int = 5,
        aspect_ratio: str = "9:16",
        style: str = "realistic",
    ) -> dict[str, Any]:
        """Submit a video generation job to Kling API."""
        if not self._api_key:
            logger.warning("KlingProvider: No API key — returning placeholder")
            return {
                "job_id": f"kling_placeholder_{int(time.time())}",
                "status": "placeholder",
                "provider": "kling",
                "message": "KLING_API_KEY not configured. Set it in .env to enable video generation.",
            }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/v1/videos/generations",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "prompt": prompt,
                        "duration": str(duration_seconds),
                        "aspect_ratio": aspect_ratio,
                        "mode": style,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "job_id": data.get("data", {}).get("task_id", "unknown"),
                    "status": "processing",
                    "provider": "kling",
                }
            except httpx.HTTPStatusError as exc:
                logger.error("Kling API error: %s %s", exc.response.status_code, exc.response.text[:200])
                raise VideoGenerationError(f"Kling API returned {exc.response.status_code}") from exc
            except Exception as exc:
                raise VideoGenerationError(f"Kling API call failed: {exc}") from exc

    async def check_status(self, job_id: str) -> dict[str, Any]:
        """Poll Kling for job completion."""
        if not self._api_key or job_id.startswith("kling_placeholder"):
            return {"job_id": job_id, "status": "placeholder", "video_url": None}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{self._base_url}/v1/videos/generations/{job_id}",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                status = data.get("status", "processing")

                video_url = None
                if status == "completed":
                    videos = data.get("videos", [])
                    if videos:
                        video_url = videos[0].get("url")

                return {
                    "job_id": job_id,
                    "status": status,
                    "video_url": video_url,
                }
            except Exception as exc:
                logger.error("Kling status check failed: %s", exc)
                return {"job_id": job_id, "status": "error", "video_url": None}

    async def download_video(self, video_url: str, output_path: str) -> str:
        """Download the generated video file."""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(video_url)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)
        return output_path
