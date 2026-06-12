from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()


def _id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_id)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    plan = Column(String, default="starter")
    credits = Column(Integer, default=500)
    rate_limit_reset = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    prompt = Column(String)
    status = Column(String, default="queued")  # queued|rendering|ready|failed
    url = Column(String, nullable=True)
    duration_s = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    kind = Column(String)  # video|content|analytics|publishing|leadgen|adops
    name = Column(String)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default=dict)


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    name = Column(String)
    nodes = Column(JSON, default=list)
    edges = Column(JSON, default=list)
    enabled = Column(Boolean, default=True)


class SocialPost(Base):
    __tablename__ = "social_posts"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    platform = Column(String)  # instagram|tiktok|youtube|...
    content = Column(String)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    status = Column(String, default="scheduled")

from .campaign import (
    Campaign,
    Persona,
    CompetitorInsight,
    Angle,
    Hook,
    Headline,
    CTA,
    AdCopy,
    CreativeConcept,
    VideoScript,
    CampaignScore,
)

from .billing import (
    Subscription,
    Payment,
    BillingEvent,
    ProcessedWebhook,
)
