from typing import Set
from fastapi import WebSocket
import base64


class WebSocketManager:

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_tts_event(self, text: str, audio_content: bytes, voice: str = "onyx"):
        """Broadcast TTS event with audio data to all connected Discord bots"""
        if not self.active_connections:
            print("No WebSocket clients connected - TTS event not sent")
            return

        # Encode audio as base64 for JSON transmission
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')

        event = {
            "event": "tts",
            "data": {
                "text": text,
                "voice": voice,
                "audio": audio_base64  # Send audio directly embedded in WebSocket message
            }
        }

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(event)
                print(f"→ Sent TTS event to Discord bot: '{text[:50]}...' ({len(audio_content)} bytes audio)")
            except Exception as e:
                print(f"✗ Error sending to client: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)

ws_manager = WebSocketManager()
