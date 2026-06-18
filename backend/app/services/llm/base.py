"""
BaseLLMProvider — abstract interface for all LLM backends.

Concrete implementations: BedrockProvider, OpenAIProvider (fallback).
All provider credentials come from app.core.config.settings — never hardcoded.
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMProviderError(Exception):
    """Raised when a provider call fails unrecoverably."""


class LLMStructuredOutputError(LLMProviderError):
    """Raised when JSON extraction from a provider response fails after all fallback attempts."""


class BaseLLMProvider(ABC):

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique lowercase identifier, e.g. 'bedrock' or 'openai'."""

    @abstractmethod
    def generate_text(self, system: str, user: str, *, model: str | None = None) -> str:
        """
        Return a raw text completion.

        Args:
            system: System-level instruction.
            user:   User-turn message.
            model:  Override the provider's default model (e.g. use Haiku instead of Sonnet).
        """

    @abstractmethod
    def generate_json(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Return a parsed JSON dict.

        The provider is responsible for prompt-engineering the JSON instruction and
        extracting the dict from the raw response.  Raises LLMStructuredOutputError
        on unrecoverable parse failure.
        """
