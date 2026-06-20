"""
Sprint 3.1C — Cost Tracking Model

Tracks Bedrock token usage and credit consumption per agent execution.
Enables cost analysis, billing accuracy, and usage dashboards.
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float
from datetime import datetime
from . import Base, _id


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id          = Column(String, primary_key=True, default=_id)
    user_id     = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id      = Column(String, nullable=True, index=True)
    campaign_id = Column(String, nullable=True, index=True)

    # What was used
    agent_type      = Column(String, nullable=False, index=True)   # e.g. "caption_agent", "seo_agent"
    provider        = Column(String, nullable=False)                # "bedrock", "openai", "kling"
    model_id        = Column(String, nullable=True)                 # e.g. "anthropic.claude-3-sonnet..."

    # Token usage (LLM)
    input_tokens    = Column(Integer, default=0)
    output_tokens   = Column(Integer, default=0)
    total_tokens    = Column(Integer, default=0)

    # Cost
    cost_usd        = Column(Float, default=0.0)    # Actual AWS/provider cost in USD
    credits_charged = Column(Integer, default=0)    # Credits charged to user

    # Timing
    duration_ms     = Column(Integer, default=0)    # Execution time in milliseconds

    # Metadata
    metadata_json   = Column(JSON, nullable=True)   # Extra info (model params, retries, etc.)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
