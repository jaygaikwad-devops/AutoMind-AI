from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base, _id

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True, nullable=True)
    job_id = Column(String, ForeignKey("campaign_jobs.id"), index=True, nullable=True)

    type = Column(String, nullable=False) # video, image, voiceover, campaign_export, thumbnail
    provider = Column(String, nullable=True) # azure_speech, kling, runway, elevenlabs, openai

    s3_key = Column(String, nullable=False, unique=True)
    cdn_url = Column(String, nullable=True)
    thumbnail_s3_key = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, processing, ready, failed, deleted

    duration_seconds = Column(Integer, default=0)
    generation_cost_usd = Column(Float, default=0.0)
    credits_used = Column(Integer, default=0)

    metadata_info = Column("metadata", JSON, default=dict) # renamed internally to avoid conflict with Base.metadata

    created_at = Column(DateTime, default=datetime.utcnow)

