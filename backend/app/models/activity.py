from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from datetime import datetime
from . import Base, _id

class ActivityEvent(Base):
    __tablename__ = "activity_events"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event = Column(String, index=True) # e.g. "campaign_generated", "video_generation_started"
    agent = Column(String, nullable=True) # e.g. "campaign_manager"
    credits_used = Column(Integer, default=0)
    job_id = Column(String, nullable=True)
    campaign_id = Column(String, nullable=True)
    asset_id = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True) # To store any additional unstructured data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
