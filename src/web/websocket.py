import weakref
from fastapi import WebSocket
from src.logger import logger, log_buffer
from src.config import MAX_WEBSOCKET_CLIENTS
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: weakref.WeakSet[WebSocket] = weakref.WeakSet()
    
    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= MAX_WEBSOCKET_CLIENTS:
            await websocket.close(code=1008)  # Policy Violation
            return False
        await websocket.accept()
        self.active_connections.add(websocket)
        return True
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.disconnect(connection)

# Crear una instancia global del WebSocketManager
ws_manager = WebSocketManager()