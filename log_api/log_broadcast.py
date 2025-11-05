from typing import List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

        async def connect(self, ws: WebSocket):
            await ws.accept()
            self.active.append(ws)

        def disconnect(self, ws: WebSocket):
            try:
                self.active.remove(ws)
            except ValueError:
                pass

        async def broadcast(self, message: dict):
            data = json.dumps(message)
            for ws in list(self.active):
                try:
                    await ws.send_text(data)
                except Exception:
                    self.disconnect(ws)

manager = ConnectionManager()