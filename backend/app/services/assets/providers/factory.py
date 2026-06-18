from .video import KlingProvider, RunwayProvider
from .voice import AzureSpeechProvider, ElevenLabsProvider
from .base import VideoProvider, VoiceProvider

class ProviderFactory:
    _video_providers = {
        "kling": KlingProvider(),
        "runway": RunwayProvider()
    }
    
    _voice_providers = {
        "azure_speech": AzureSpeechProvider(),
        "elevenlabs": ElevenLabsProvider()
    }

    @classmethod
    def get_video_provider(cls, provider_id: str) -> VideoProvider:
        provider = cls._video_providers.get(provider_id.lower())
        if not provider:
            raise ValueError(f"Unknown video provider: {provider_id}")
        return provider

    @classmethod
    def get_voice_provider(cls, provider_id: str) -> VoiceProvider:
        provider = cls._voice_providers.get(provider_id.lower())
        if not provider:
            raise ValueError(f"Unknown voice provider: {provider_id}")
        return provider
