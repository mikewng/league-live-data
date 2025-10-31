"""
WebSocket client service to connect Discord bot to FastAPI backend
Listens for TTS events and triggers audio playback
"""
import asyncio
import websockets
import json
import os


class BackendWebSocketClient:
    """WebSocket client that connects to backend and handles TTS events"""

    def __init__(self, bot):
        self.bot = bot
        self.websocket = None
        self.backend_url = os.getenv("BACKEND_WS_URL", "ws://localhost:8000/ws/discord")
        self.running = False
        self.reconnect_delay = 5  # seconds

    async def start(self):
        """Start the WebSocket client and maintain connection"""
        self.running = True
        print(f"🔌 Starting WebSocket client for backend: {self.backend_url}")

        while self.running:
            try:
                await self._connect_and_listen()
            except Exception as e:
                print(f"❌ WebSocket error: {e}")

            if self.running:
                print(f"🔄 Reconnecting in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)

    async def _connect_and_listen(self):
        """Connect to backend WebSocket and listen for events"""
        try:
            async with websockets.connect(self.backend_url) as websocket:
                self.websocket = websocket
                print(f"✅ Connected to backend WebSocket: {self.backend_url}")

                # Send initial ping
                await websocket.send("ping")

                # Listen for events
                async for message in websocket:
                    await self._handle_message(message)

        except websockets.exceptions.ConnectionClosed:
            print("⚠ WebSocket connection closed")
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
        finally:
            self.websocket = None

    async def _handle_message(self, message: str):
        """Handle incoming WebSocket messages from backend"""
        try:
            # Parse JSON message
            data = json.loads(message)
            event_type = data.get("event")

            if event_type == "tts":
                await self._handle_tts_event(data.get("data", {}))
            else:
                print(f"⚠ Unknown event type: {event_type}")

        except json.JSONDecodeError:
            # Handle non-JSON messages (like "pong")
            if message == "pong":
                print("🏓 Received pong from backend")
            else:
                print(f"⚠ Received non-JSON message: {message}")
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    async def _handle_tts_event(self, data: dict):
        """Handle TTS event from backend"""
        text = data.get("text", "")
        voice = data.get("voice", "onyx")
        audio_base64 = data.get("audio", "")

        print(f"🎤 Received TTS event: '{text[:50]}...' (voice: {voice})")

        # Get the TTS cog
        tts_cog = self.bot.get_cog("TextToSpeechCogCommands")

        if not tts_cog:
            print("❌ TTS cog not found")
            return

        # Decode audio from base64
        if audio_base64:
            import base64
            try:
                audio_data = base64.b64decode(audio_base64)
                print(f"✓ Decoded audio data ({len(audio_data)} bytes)")
                await tts_cog.play_tts_audio(audio_data)
            except Exception as e:
                print(f"❌ Failed to decode audio: {e}")
        else:
            print("❌ No audio data in TTS event")

    async def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
        print("🛑 WebSocket client stopped")

    async def send_ping(self):
        """Send ping to backend to keep connection alive"""
        if self.websocket:
            try:
                await self.websocket.send("ping")
            except Exception as e:
                print(f"❌ Error sending ping: {e}")
