import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import get_settings
from ..utils.ws_broadcast import get_redis

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, analysis_id: str, websocket: WebSocket):
        await websocket.accept()
        if analysis_id not in self.active:
            self.active[analysis_id] = []
        self.active[analysis_id].append(websocket)

    def disconnect(self, analysis_id: str, websocket: WebSocket):
        if analysis_id in self.active:
            self.active[analysis_id] = [
                ws for ws in self.active[analysis_id] if ws != websocket
            ]

    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{analysis_id}")
async def websocket_endpoint(websocket: WebSocket, analysis_id: str):
    await manager.connect(analysis_id, websocket)
    settings = get_settings()
    r = get_redis()
    pubsub = r.pubsub()
    channel = f"analysis:{analysis_id}"
    pubsub.subscribe(channel)

    try:
        await websocket.send_json(
            {"event": "connected", "analysis_id": analysis_id}
        )

        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

            try:
                client_msg = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.05
                )
                if client_msg == "ping":
                    await websocket.send_json({"event": "pong"})
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(analysis_id, websocket)
        pubsub.unsubscribe(channel)
        pubsub.close()
