"""
WebSocket gateway — streams real ActivityEvent data to authenticated users.
Replaces the previous random.randint mock implementation.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.future import select
from sqlalchemy import desc
import asyncio
import json
import logging

from app.db import AsyncSessionLocal
from app.core.security import decode_token
from app.models.activity import ActivityEvent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/live")
async def live(ws: WebSocket, token: str = Query(default=None)):
    """
    Authenticated WebSocket that streams recent activity events.
    Connect with: ws://host/ws/live?token=<jwt>
    Or sends cookie-based auth (access_token cookie).
    """
    await ws.accept()

    # Authenticate
    auth_token = token or ws.cookies.get("access_token")
    if not auth_token:
        await ws.send_text(json.dumps({"type": "error", "message": "Not authenticated"}))
        await ws.close(code=4001)
        return

    try:
        user_id = decode_token(auth_token)
    except Exception:
        await ws.send_text(json.dumps({"type": "error", "message": "Invalid token"}))
        await ws.close(code=4001)
        return

    last_event_id = None

    try:
        while True:
            # Query recent events for this user
            async with AsyncSessionLocal() as db:
                query = (
                    select(ActivityEvent)
                    .filter(ActivityEvent.user_id == user_id)
                    .order_by(desc(ActivityEvent.timestamp))
                    .limit(10)
                )
                if last_event_id:
                    # Only send events newer than what client already has
                    query = query.filter(ActivityEvent.id != last_event_id)

                result = await db.execute(query)
                events = result.scalars().all()

            if events:
                last_event_id = events[0].id
                payload = [
                    {
                        "id": e.id,
                        "event": e.event,
                        "agent": e.agent,
                        "credits_used": e.credits_used,
                        "campaign_id": e.campaign_id,
                        "metadata": e.metadata_json,
                        "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    }
                    for e in events
                ]
                await ws.send_text(json.dumps({"type": "events", "data": payload}))
            else:
                await ws.send_text(json.dumps({"type": "heartbeat"}))

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        return
    except Exception as exc:
        logger.warning("WebSocket error for user %s: %s", user_id, exc)
        return
