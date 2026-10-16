import asyncio
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Mapea id_vehiculo -> Lista de WebSockets activos
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Bloqueos para evitar dos DEMOs simultáneas por vehículo
        self.active_demos: Dict[int, bool] = {}

    async def connect(self, websocket: WebSocket, id_vehiculo: int):
        await websocket.accept()
        if id_vehiculo not in self.active_connections:
            self.active_connections[id_vehiculo] = []
        self.active_connections[id_vehiculo].append(websocket)

    def disconnect(self, websocket: WebSocket, id_vehiculo: int):
        if id_vehiculo in self.active_connections:
            if websocket in self.active_connections[id_vehiculo]:
                self.active_connections[id_vehiculo].remove(websocket)

    async def broadcast(self, id_vehiculo: int, message: dict):
        if id_vehiculo in self.active_connections:
            for connection in self.active_connections[id_vehiculo]:
                await connection.send_json(message)

manager = ConnectionManager()