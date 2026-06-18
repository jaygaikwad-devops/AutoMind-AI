from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Returns the unique identifier for the provider (e.g., 'kling')."""
        pass

class VideoProvider(BaseProvider):
    @abstractmethod
    async def generate_video(self, prompt: str, **kwargs) -> str:
        """Generates a video and returns an asset reference or URL."""
        pass

class VoiceProvider(BaseProvider):
    @abstractmethod
    async def generate_voiceover(self, text: str, **kwargs) -> str:
        """Generates a voiceover and returns an asset reference or URL."""
        pass
