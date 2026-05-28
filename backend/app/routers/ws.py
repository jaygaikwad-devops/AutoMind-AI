from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio, json, random

router = APIRouter()


@router.websocket("/live")
async def live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps({
                "type": "tick",
                "engagement": random.randint(40, 100),
                "leads": random.randint(0, 8),
            }))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        return
