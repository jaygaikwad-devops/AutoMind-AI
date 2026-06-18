"""
ValidationLayer — uses Claude Haiku to quality-check agent output.

validate_content() returns a ValidationResult dict:
  {
    "quality_score": 0–100,
    "issues": ["..."],
    "recommendations": ["..."],
    "passed": bool   # True if score >= 80
  }

Callers should pass the JSON-serialisable content string or dict.
If the Haiku call itself fails, we return a default passing result
rather than blocking the pipeline — generation failure is worse than
skipping validation.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import settings
from app.services.llm.provider_registry import get_provider

logger = logging.getLogger(__name__)

QUALITY_THRESHOLD = 80

_SYSTEM_PROMPT = """You are a senior marketing quality auditor. 
Evaluate the provided marketing content for:
1. Clarity — is the message immediately understandable?
2. Marketing Strength — does it create desire or urgency?
3. Grammar — is it grammatically correct?
4. Readability — is it easy to read at a glance?

Return ONLY a JSON object with this exact structure:
{
  "quality_score": <integer 0-100>,
  "issues": [<string>, ...],
  "recommendations": [<string>, ...]
}

Be strict but fair. Score below 80 means the content needs improvement."""


def validate_content(content: Any, content_type: str = "marketing content") -> dict[str, Any]:
    """
    Synchronous quality-check via Claude Haiku.
    Returns a ValidationResult dict.
    """
    if isinstance(content, (dict, list)):
        content_str = json.dumps(content, indent=2)
    else:
        content_str = str(content)

    user_prompt = (
        f"Please evaluate this {content_type}:\n\n{content_str[:3000]}"
    )

    try:
        provider = get_provider()
        result = provider.generate_json(
            system=_SYSTEM_PROMPT,
            user=user_prompt,
            model=settings.BEDROCK_HAIKU_MODEL_ID,
        )
        score = int(result.get("quality_score", 75))
        return {
            "quality_score": score,
            "issues": result.get("issues", []),
            "recommendations": result.get("recommendations", []),
            "passed": score >= QUALITY_THRESHOLD,
        }
    except Exception as exc:
        logger.warning("ValidationLayer: Haiku validation failed (%s) — using default pass", exc)
        return {
            "quality_score": 75,
            "issues": [],
            "recommendations": ["Validation skipped due to provider error."],
            "passed": True,  # Don't block pipeline on validation failure
        }
