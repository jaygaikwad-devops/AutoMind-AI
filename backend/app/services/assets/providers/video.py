from .base import VideoProvider

class KlingProvider(VideoProvider):
    @property
    def provider_id(self) -> str:
        return "kling"

    async def generate_video(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("KlingProvider is a placeholder for Sprint 3")

class RunwayProvider(VideoProvider):
    @property
    def provider_id(self) -> str:
        return "runway"

    async def generate_video(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("RunwayProvider is a placeholder for Sprint 3")
