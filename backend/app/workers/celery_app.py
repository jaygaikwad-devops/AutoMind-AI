from celery import Celery
from app.core.config import settings

celery_app = Celery("automind", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


@celery_app.task
def render_video(video_id: str, prompt: str) -> dict:
    # TODO: call AI video provider, store to S3
    return {"video_id": video_id, "status": "ready", "url": f"https://cdn.automind.ai/{video_id}.mp4"}


@celery_app.task
def publish_post(post_id: str, platform: str, content: str) -> dict:
    # TODO: call platform API
    return {"post_id": post_id, "platform": platform, "status": "published"}
