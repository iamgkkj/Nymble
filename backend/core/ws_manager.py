from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Maps token -> list of active WebSocket connections for private chat
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Maps board_name -> list of active WebSocket connections for group chat
        self.board_connections: Dict[str, List[WebSocket]] = {}

    # --- Private Chat ---
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

    # --- Board Chat ---
    async def connect_board(self, board_name: str, websocket: WebSocket):
        await websocket.accept()
        if board_name not in self.board_connections:
            self.board_connections[board_name] = []
        self.board_connections[board_name].append(websocket)

    def disconnect_board(self, board_name: str, websocket: WebSocket):
        if board_name in self.board_connections:
            if websocket in self.board_connections[board_name]:
                self.board_connections[board_name].remove(websocket)
            if not self.board_connections[board_name]:
                del self.board_connections[board_name]

    async def broadcast_board(self, message: dict, board_name: str):
        if board_name in self.board_connections:
            for connection in self.board_connections[board_name]:
                await connection.send_json(message)

manager = ConnectionManager()
