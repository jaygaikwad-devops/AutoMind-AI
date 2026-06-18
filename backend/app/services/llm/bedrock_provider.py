"""
BedrockProvider — AWS Bedrock (Anthropic Claude) implementation.

Model routing:
  generate_text / generate_json default → settings.BEDROCK_MODEL_ID    (Claude Sonnet)
  Pass model=settings.BEDROCK_HAIKU_MODEL_ID explicitly for validation  (Claude Haiku)

All credentials come from environment variables; boto3 reads them automatically
from AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN or the EC2
instance profile.  No credentials are ever hardcoded.
"""
import json
import re
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from .base import BaseLLMProvider, LLMProviderError, LLMStructuredOutputError

logger = logging.getLogger(__name__)


class BedrockProvider(BaseLLMProvider):
    """
    Wraps the AWS Bedrock `invoke_model` API for Anthropic Claude models.

    Thread-safety: boto3 clients are not thread-safe; we create one client per
    instance.  In a FastAPI async context this is called from a thread-pool
    executor (run_in_executor), so each call gets its own stack frame.
    """

    def __init__(self) -> None:
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.BEDROCK_REGION,
            # Credentials resolved automatically from env / instance-profile
        )
        self._default_model = settings.BEDROCK_MODEL_ID

    # ------------------------------------------------------------------
    # BaseLLMProvider interface
    # ------------------------------------------------------------------

    @property
    def provider_id(self) -> str:
        return "bedrock"

    def generate_text(self, system: str, user: str, *, model: str | None = None) -> str:
        return self._invoke(system=system, user=user, model=model or self._default_model)

    def generate_json(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
    ) -> dict[str, Any]:
        json_system = (
            system
            + "\n\nYou MUST respond with ONLY valid JSON. "
            "Do NOT include markdown code fences, explanations, or any text outside the JSON object."
        )
        raw = self._invoke(
            system=json_system,
            user=user,
            model=model or self._default_model,
        )
        return self._extract_json(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _invoke(self, system: str, user: str, model: str) -> str:
        """Call invoke_model and return the assistant's text content."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        try:
            response = self._client.invoke_model(
                modelId=model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
        except (BotoCoreError, ClientError) as exc:
            logger.error("Bedrock invoke_model failed: %s", exc)
            raise LLMProviderError(f"Bedrock API error: {exc}") from exc

    def _extract_json(self, raw: str) -> dict[str, Any]:
        """
        Three-stage JSON extraction from a raw text response.

        Stage 1: json.loads() on the full string.
        Stage 2: Strip markdown fences (```json ... ```) then json.loads().
        Stage 3: Regex-find the first {...} or [...] block then json.loads().

        Raises LLMStructuredOutputError if all three fail.
        """
        # Stage 1 — direct parse
        text = raw.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Stage 2 — strip markdown fences
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence_match:
            try:
                return json.loads(fence_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Stage 3 — find first balanced { } or [ ]
        brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass

        logger.error("BedrockProvider: all JSON extraction attempts failed. Raw: %.300s", raw)
        raise LLMStructuredOutputError(
            f"Could not extract JSON from Bedrock response. Raw (truncated): {raw[:300]}"
        )
