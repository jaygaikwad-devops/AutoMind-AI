"""
OpenAIProvider — fallback provider using the OpenAI Python SDK.

Used when settings.LLM_PROVIDER == 'openai'.
"""
import json
import logging
from typing import Any

from app.core.config import settings
from .base import BaseLLMProvider, LLMProviderError, LLMStructuredOutputError

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):

    def __init__(self) -> None:
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError as exc:
            raise ImportError("openai package is required for OpenAIProvider") from exc
        self._default_model = "gpt-4o-mini"

    @property
    def provider_id(self) -> str:
        return "openai"

    def generate_text(self, system: str, user: str, *, model: str | None = None) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=model or self._default_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            raise LLMProviderError(f"OpenAI API error: {exc}") from exc

    def generate_json(self, system: str, user: str, *, model: str | None = None) -> dict[str, Any]:
        json_system = (
            system
            + "\n\nRespond ONLY with valid JSON. No markdown fences or prose outside the JSON."
        )
        raw = self.generate_text(json_system, user, model=model)
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            import re
            m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    pass
            raise LLMStructuredOutputError(f"OpenAI JSON extraction failed. Raw: {raw[:300]}")
