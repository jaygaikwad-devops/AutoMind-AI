"""
Sprint 3.1B — CompetitorSnapshot Model

Stores competitive intelligence (positioning, strengths, weaknesses,
messaging angles, content opportunities) per industry with 24-hour TTL.

Cache logic: query WHERE industry = ? AND expires_at > NOW().
If expired or missing → regenerate via Bedrock, persist, return fresh.
"""
from sqlalchemy import Column, String, DateTime, JSON, Float, Text, Index
from datetime import datetime, timedelta
from . import Base, _id


def _default_expires_at():
    return datetime.utcnow() + timedelta(hours=24)


class CompetitorSnapshot(Base):
    __tablename__ = "competitor_snapshots"
    __table_args__ = (
        Index("ix_competitor_snapshots_industry", "industry"),
        Index("ix_competitor_snapshots_name", "competitor_name"),
        Index("ix_competitor_snapshots_industry_expires", "industry", "expires_at"),
    )

    id                      = Column(String, primary_key=True, default=_id)
    industry                = Column(String, nullable=False)
    competitor_name         = Column(String, nullable=False)

    # Intelligence data (Bedrock-generated)
    positioning             = Column(Text, nullable=True)
    strengths_json          = Column(JSON, nullable=True)    # list[str]
    weaknesses_json         = Column(JSON, nullable=True)    # list[str]
    messaging_angles_json   = Column(JSON, nullable=True)    # list[str]
    content_opportunities_json = Column(JSON, nullable=True) # list[str]
    keywords_json           = Column(JSON, nullable=True)    # list[str]

    # Quality indicator
    confidence_score        = Column(Float, nullable=True)   # 0.0–1.0

    # TTL management
    created_at              = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at              = Column(DateTime, default=_default_expires_at, nullable=False)
