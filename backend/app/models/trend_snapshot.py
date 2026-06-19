"""
Sprint 3.1B — TrendSnapshot Model

Stores trending keywords, hashtags, content formats, and CTA styles
per industry/platform with a 24-hour database-level TTL.

Cache logic: query WHERE industry = ? AND expires_at > NOW().
If expired or missing → regenerate via Bedrock, persist, return fresh.
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON, Float, Index
from datetime import datetime, timedelta
from . import Base, _id


def _default_expires_at():
    return datetime.utcnow() + timedelta(hours=24)


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"
    __table_args__ = (
        Index("ix_trend_snapshots_industry", "industry"),
        Index("ix_trend_snapshots_expires_at", "expires_at"),
        Index("ix_trend_snapshots_industry_expires", "industry", "expires_at"),
    )

    id                  = Column(String, primary_key=True, default=_id)
    industry            = Column(String, nullable=False)
    platform            = Column(String, nullable=False)  # instagram|tiktok|linkedin|youtube|twitter|google

    # Intelligence data (Bedrock-generated)
    keywords_json       = Column(JSON, nullable=True)     # list[str] — trending keywords
    hashtags_json       = Column(JSON, nullable=True)     # list[str] — trending hashtags
    content_formats_json = Column(JSON, nullable=True)    # list[str] — e.g. ["carousel", "short-form video"]
    cta_styles_json     = Column(JSON, nullable=True)     # list[str] — e.g. ["urgency", "social proof"]

    # Quality indicator
    confidence_score    = Column(Float, nullable=True)    # 0.0–1.0

    # TTL management
    captured_at         = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at          = Column(DateTime, default=_default_expires_at, nullable=False)
