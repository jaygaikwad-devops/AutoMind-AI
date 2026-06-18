"""
Sprint 3.1A — Marketing intelligence models.

ResearchSnapshot  : persists raw web-scrape + Bedrock research output per campaign.
BrandProfile      : user-scoped brand identity, injected into all LLM prompts.
CampaignContent   : generic envelope storing any agent-produced content as JSON,
                    with quality score from the Haiku validation pass.
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float, Text
from datetime import datetime
from . import Base, _id


class ResearchSnapshot(Base):
    __tablename__ = "research_snapshots"

    id              = Column(String, primary_key=True, default=_id)
    campaign_id     = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), index=True, nullable=True)
    user_id         = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    # Input
    website_url     = Column(String, nullable=True)
    product_name    = Column(String, nullable=True)
    industry        = Column(String, nullable=True)

    # Bedrock-generated research fields
    company_summary      = Column(Text, nullable=True)
    market_position      = Column(Text, nullable=True)
    core_benefits        = Column(JSON, nullable=True)   # list[str]
    competitor_summary   = Column(Text, nullable=True)
    extracted_keywords   = Column(JSON, nullable=True)   # list[str]
    target_audience_summary = Column(Text, nullable=True)

    # Raw scrape data (from analyze_website)
    scraped_title       = Column(String, nullable=True)
    scraped_description = Column(Text, nullable=True)
    scraped_h1          = Column(JSON, nullable=True)
    scraped_main_text   = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id          = Column(String, primary_key=True, default=_id)
    user_id     = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    brand_name      = Column(String, nullable=False)
    website_url     = Column(String, nullable=True)
    industry        = Column(String, nullable=True)
    tone            = Column(JSON, nullable=True)    # list[str] e.g. ["professional", "witty"]
    target_audience = Column(Text, nullable=True)
    brand_colors    = Column(JSON, nullable=True)    # {"primary": "#hex", "secondary": "#hex"}
    is_default      = Column(Integer, default=0)    # 0/1 — one default per user

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)


class CampaignContent(Base):
    __tablename__ = "campaign_content"

    id          = Column(String, primary_key=True, default=_id)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), index=True, nullable=True)
    user_id     = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id      = Column(String, nullable=True)   # FK to campaign_jobs; loose ref — avoid circular dep

    # Content classification
    content_type = Column(String, nullable=False, index=True)
    # content_type values: "persona" | "hooks" | "research" | "ad_copy" | "campaign_score"

    # The actual generated content
    content_json    = Column(JSON, nullable=False)

    # Validation results from Claude Haiku
    quality_score   = Column(Integer, nullable=True)    # 0–100
    validation_json = Column(JSON, nullable=True)       # {"issues": [], "recommendations": []}
    validation_passed = Column(Integer, default=0)      # 0/1

    created_at = Column(DateTime, default=datetime.utcnow)
