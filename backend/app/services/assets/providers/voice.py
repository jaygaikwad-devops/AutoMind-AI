from .base import VoiceProvider

class AzureSpeechProvider(VoiceProvider):
    @property
    def provider_id(self) -> str:
        return "azure_speech"

    async def generate_voiceover(self, text: str, **kwargs) -> str:
        raise NotImplementedError("AzureSpeechProvider is a placeholder for Sprint 3")

class ElevenLabsProvider(VoiceProvider):
    @property
    def provider_id(self) -> str:
        return "elevenlabs"

    async def generate_voiceover(self, text: str, **kwargs) -> str:
        raise NotImplementedError("ElevenLabsProvider is a placeholder for Sprint 3")
