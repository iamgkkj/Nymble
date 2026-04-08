from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Maps token -> list of active WebSocket connections
        # A single user token could technically have multiple tabs open
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, token: str, websocket: WebSocket):
        await websocket.accept()
        if token not in self.active_connections:
            self.active_connections[token] = []
        self.active_connections[token].append(websocket)

    def disconnect(self, token: str, websocket: WebSocket):
        if token in self.active_connections:
            if websocket in self.active_connections[token]:
                self.active_connections[token].remove(websocket)
            if not self.active_connections[token]:
                del self.active_connections[token]

    async def send_personal_message(self, message: dict, token: str):
        if token in self.active_connections:
            for connection in self.active_connections[token]:
                await connection.send_json(message)

manager = ConnectionManager()
