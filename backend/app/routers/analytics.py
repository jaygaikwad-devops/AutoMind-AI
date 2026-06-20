"""
Analytics router — real data from ActivityEvent and UsageLog.
Replaces hardcoded mock data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.models import User
from app.models.activity import ActivityEvent
from app.models.cost_tracking import UsageLog
from app.models.marketing import CampaignContent
from app.api.deps import get_current_user
from app.db import get_db

router = APIRouter()


@router.get("/overview")
async def overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Real analytics from user's activity and usage data."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Total content generated (all time)
    content_count_result = await db.execute(
        select(func.count(CampaignContent.id)).filter(CampaignContent.user_id == current_user.id)
    )
    total_content = content_count_result.scalar() or 0

    # Content generated today
    today_content_result = await db.execute(
        select(func.count(CampaignContent.id)).filter(
            CampaignContent.user_id == current_user.id,
            CampaignContent.created_at >= today_start,
        )
    )
    content_today = today_content_result.scalar() or 0

    # Total credits consumed (from UsageLog)
    credits_result = await db.execute(
        select(func.sum(UsageLog.credits_charged)).filter(UsageLog.user_id == current_user.id)
    )
    total_credits_used = credits_result.scalar() or 0

    # Credits used last 7 days
    credits_7d_result = await db.execute(
        select(func.sum(UsageLog.credits_charged)).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.created_at >= last_7d,
        )
    )
    credits_last_7d = credits_7d_result.scalar() or 0

    # Recent activity count (last 24h)
    activity_result = await db.execute(
        select(func.count(ActivityEvent.id)).filter(
            ActivityEvent.user_id == current_user.id,
            ActivityEvent.timestamp >= last_24h,
        )
    )
    activities_24h = activity_result.scalar() or 0

    # Average quality score
    quality_result = await db.execute(
        select(func.avg(CampaignContent.quality_score)).filter(
            CampaignContent.user_id == current_user.id,
            CampaignContent.quality_score.isnot(None),
        )
    )
    avg_quality = round(quality_result.scalar() or 0, 1)

    return {
        "total_content_generated": total_content,
        "content_today": content_today,
        "total_credits_used": total_credits_used,
        "credits_last_7d": credits_last_7d,
        "activities_24h": activities_24h,
        "avg_quality_score": avg_quality,
        "credits_remaining": current_user.credits,
        "plan": current_user.plan,
    }


@router.get("/activity")
async def recent_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the 20 most recent activity events for the current user."""
    result = await db.execute(
        select(ActivityEvent)
        .filter(ActivityEvent.user_id == current_user.id)
        .order_by(ActivityEvent.timestamp.desc())
        .limit(20)
    )
    events = result.scalars().all()
    return [
        {
            "id": e.id,
            "event": e.event,
            "agent": e.agent,
            "credits_used": e.credits_used,
            "job_id": e.job_id,
            "campaign_id": e.campaign_id,
            "metadata": e.metadata_json,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


@router.get("/usage")
async def usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns usage breakdown by agent type."""
    result = await db.execute(
        select(
            UsageLog.agent_type,
            func.count(UsageLog.id).label("call_count"),
            func.sum(UsageLog.credits_charged).label("total_credits"),
            func.avg(UsageLog.duration_ms).label("avg_duration_ms"),
        )
        .filter(UsageLog.user_id == current_user.id)
        .group_by(UsageLog.agent_type)
    )
    rows = result.all()
    return [
        {
            "agent_type": row.agent_type,
            "call_count": row.call_count,
            "total_credits": row.total_credits or 0,
            "avg_duration_ms": round(row.avg_duration_ms or 0),
        }
        for row in rows
    ]


@router.get("/content")
async def content_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns content breakdown by type with quality scores."""
    result = await db.execute(
        select(
            CampaignContent.content_type,
            func.count(CampaignContent.id).label("count"),
            func.avg(CampaignContent.quality_score).label("avg_quality"),
        )
        .filter(CampaignContent.user_id == current_user.id)
        .group_by(CampaignContent.content_type)
    )
    rows = result.all()
    return [
        {
            "content_type": row.content_type,
            "count": row.count,
            "avg_quality": round(row.avg_quality or 0, 1),
        }
        for row in rows
    ]
