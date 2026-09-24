from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, well_id: str, websocket: WebSocket):
        await websocket.accept()
        if well_id not in self.active_connections:
            self.active_connections[well_id] = []
        self.active_connections[well_id].append(websocket)

    def disconnect(self, well_id: str, websocket: WebSocket):
        if well_id in self.active_connections:
            if websocket in self.active_connections[well_id]:
                self.active_connections[well_id].remove(websocket)

    async def broadcast_telemetry(self, well_id: str, data: dict):
        if well_id in self.active_connections:
            for connection in self.active_connections[well_id]:
                await connection.send_json(data)

manager = ConnectionManager()

@router.websocket("/ws/drilling/{well_id}")
async def websocket_drilling_endpoint(websocket: WebSocket, well_id: str):
    await manager.connect(well_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast telemetry to connected clients
            await manager.broadcast_telemetry(well_id, data)
    except WebSocketDisconnect:
        manager.disconnect(well_id, websocket)
    except Exception as e:
        manager.disconnect(well_id, websocket)