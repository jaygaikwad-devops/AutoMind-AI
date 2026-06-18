"""
LLMProviderRegistry — resolves the active LLM provider from settings.LLM_PROVIDER.

Call get_provider() to obtain a BaseLLMProvider instance.
Providers are lazily instantiated on first access.
"""
import logging
from .base import BaseLLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

_registry: dict[str, BaseLLMProvider] = {}


def _build_registry() -> dict[str, BaseLLMProvider]:
    from app.core.config import settings
    from .bedrock_provider import BedrockProvider
    from .openai_provider import OpenAIProvider

    reg: dict[str, BaseLLMProvider] = {}
    try:
        reg["bedrock"] = BedrockProvider()
    except Exception as exc:
        logger.warning("BedrockProvider init failed (will be unavailable): %s", exc)
    try:
        reg["openai"] = OpenAIProvider()
    except Exception as exc:
        logger.warning("OpenAIProvider init failed (will be unavailable): %s", exc)
    return reg


def get_provider(provider_id: str | None = None) -> BaseLLMProvider:
    """
    Return a BaseLLMProvider for the given provider_id.
    Falls back to settings.LLM_PROVIDER if provider_id is None.
    """
    global _registry
    if not _registry:
        _registry = _build_registry()

    from app.core.config import settings
    pid = provider_id or settings.LLM_PROVIDER
    provider = _registry.get(pid)
    if provider is None:
        raise LLMProviderError(
            f"LLM provider '{pid}' is not available. "
            f"Registered providers: {list(_registry.keys())}"
        )
    return provider
