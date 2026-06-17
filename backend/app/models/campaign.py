from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base, _id

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    website_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    product_description = Column(Text, nullable=True)
    brand_information = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    campaign_goal = Column(String, nullable=True)
    status = Column(String, default="analyzing") # analyzing, generating_personas, completed
    created_at = Column(DateTime, default=datetime.utcnow)

class CampaignJob(Base):
    __tablename__ = "campaign_jobs"
    id = Column(String, primary_key=True, default=_id)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), index=True, nullable=True)
    job_type = Column(String, index=True) # e.g. "campaign_generation", "video_generation"
    status = Column(String, default="pending", index=True) # pending, running, completed, failed
    credits_reserved = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Persona(Base):
    __tablename__ = "personas"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    name = Column(String)
    demographics = Column(String)
    job_role = Column(String)
    pain_points = Column(JSON)
    goals = Column(JSON)
    motivations = Column(JSON)
    buying_triggers = Column(JSON)
    objections = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class CompetitorInsight(Base):
    __tablename__ = "competitor_insights"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    competitors = Column(JSON)
    opportunities = Column(JSON)
    positioning = Column(Text)
    messaging_gaps = Column(JSON)
    feature_gaps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Angle(Base):
    __tablename__ = "angles"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Hook(Base):
    __tablename__ = "hooks"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    type = Column(String) # Curiosity, Pain, Emotional, Fear, Authority, Contrarian
    content = Column(Text)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Headline(Base):
    __tablename__ = "headlines"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    platform = Column(String) # Meta, LinkedIn, Google
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CTA(Base):
    __tablename__ = "ctas"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    type = Column(String) # Direct, Soft, Urgency, Demo, Trial
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdCopy(Base):
    __tablename__ = "ad_copies"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    platform = Column(String) # Meta Ads, LinkedIn Ads, Google Search Ads, Google Display Ads
    problem = Column(Text)
    agitation = Column(Text)
    solution = Column(Text)
    benefits = Column(Text)
    cta = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CreativeConcept(Base):
    __tablename__ = "creative_concepts"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    concept_name = Column(String)
    visual_direction = Column(Text)
    marketing_goal = Column(String)
    storyboard = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class VideoScript(Base):
    __tablename__ = "video_scripts"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    platform = Column(String) # TikTok, Instagram Reel, LinkedIn Video, YouTube Shorts, UGC Ad
    hook = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    timestamps = Column(JSON) # e.g. [{"time": "0:00-0:03", "action": "Zoom in on face"}]
    created_at = Column(DateTime, default=datetime.utcnow)

class CampaignScore(Base):
    __tablename__ = "campaign_scores"
    id = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id"), index=True)
    score = Column(Integer)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
