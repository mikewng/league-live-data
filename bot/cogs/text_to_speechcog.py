import discord
from discord.ext import commands
import asyncio
import aiohttp
import io
import os
import tempfile


class TextToSpeechCogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.audio_queue = asyncio.Queue()
        self.is_playing = False
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.connection_lock = asyncio.Lock()  # Prevent concurrent connections
        self.connecting = False  # Flag to track connection state

    @discord.slash_command(name="connect_vc", description="Connect the bot to your voice channel for TTS output")
    async def join_vc(self, ctx: discord.ApplicationContext):
        # Defer the response immediately to prevent timeout
        await ctx.defer()

        # Check if already connecting
        if self.connecting:
            await ctx.followup.send("⚠ Already connecting to voice channel, please wait...", ephemeral=True)
            return

        async with self.connection_lock:
            self.connecting = True
            try:
                if not ctx.author.voice:
                    await ctx.followup.send("❌ You need to be in a voice channel first!", ephemeral=True)
                    return

                channel = ctx.author.voice.channel

                # Check if bot is already connected anywhere
                if ctx.voice_client is not None:
                    if ctx.voice_client.channel == channel:
                        await ctx.followup.send(f"✅ Already connected to {channel.name}", ephemeral=True)
                        self.voice_client = ctx.voice_client
                        return
                    else:
                        # Move to new channel
                        print(f"🔄 Moving to {channel.name}...")
                        await ctx.voice_client.move_to(channel)
                        self.voice_client = ctx.voice_client
                        await ctx.followup.send(f"✅ Moved to {channel.name}")
                        return

                # Disconnect any existing connection first
                if self.voice_client and self.voice_client.is_connected():
                    print("⚠ Disconnecting existing voice client")
                    await self.voice_client.disconnect(force=True)
                    self.voice_client = None
                    await asyncio.sleep(0.5)  # Wait a bit before reconnecting

                # Connect to voice channel
                print(f"🔌 Attempting to connect to {channel.name}...")
                self.voice_client = await channel.connect(timeout=10.0, reconnect=False)

                # Verify connection
                if self.voice_client and self.voice_client.is_connected():
                    print(f"✅ Successfully connected to voice channel: {channel.name}")
                    print(f"   Voice client ID: {id(self.voice_client)}")
                    print(f"   Connected: {self.voice_client.is_connected()}")

                    await ctx.followup.send(f"✅ Connected to {channel.name}! Ready for TTS audio.")

                    # Start audio playback task only once
                    if not self.is_playing:
                        print("🎵 Starting audio playback task...")
                        self.bot.loop.create_task(self._audio_playback_task())
                    else:
                        print("🎵 Audio playback task already running")
                else:
                    print(f"❌ Voice client connection failed")
                    await ctx.followup.send(f"❌ Failed to maintain connection to {channel.name}", ephemeral=True)

            except discord.ClientException as e:
                error_msg = str(e)
                print(f"❌ ClientException during voice connection: {error_msg}")

                # Handle the 4006 error (session no longer valid)
                if "4006" in error_msg or "Session" in error_msg:
                    print("⚠ Detected stale session (error 4006). Attempting cleanup and retry...")
                    # Force cleanup any existing voice clients
                    for vc in self.bot.voice_clients:
                        try:
                            await vc.disconnect(force=True)
                        except:
                            pass
                    self.voice_client = None
                    await asyncio.sleep(1)

                    # Retry connection once
                    try:
                        print(f"🔌 Retrying connection to {channel.name}...")
                        self.voice_client = await channel.connect(timeout=10.0, reconnect=False)
                        if self.voice_client and self.voice_client.is_connected():
                            print(f"✅ Successfully connected on retry!")
                            await ctx.followup.send(f"✅ Connected to {channel.name}! Ready for TTS audio.")
                            if not self.is_playing:
                                self.bot.loop.create_task(self._audio_playback_task())
                        else:
                            await ctx.followup.send(f"❌ Failed to connect after retry. Please restart the bot.", ephemeral=True)
                    except Exception as retry_error:
                        print(f"❌ Retry failed: {retry_error}")
                        await ctx.followup.send(f"❌ Connection failed. Please restart the bot and try again.", ephemeral=True)
                else:
                    await ctx.followup.send(f"❌ Already connected to a voice channel. Use /disconnect_vc first.", ephemeral=True)

            except Exception as e:
                print(f"❌ Exception during voice connection: {e}")
                import traceback
                traceback.print_exc()
                await ctx.followup.send(f"❌ Failed to connect: {str(e)}", ephemeral=True)
            finally:
                self.connecting = False

    @discord.slash_command(name="cleanup_vc", description="Force cleanup all voice connections (use if bot is stuck)")
    async def cleanup_vc(self, ctx: discord.ApplicationContext):
        """Force cleanup all voice connections"""
        await ctx.defer()

        try:
            print("🧹 Forcing cleanup of all voice clients...")
            count = 0

            # Disconnect all voice clients
            for vc in self.bot.voice_clients:
                try:
                    await vc.disconnect(force=True)
                    count += 1
                except Exception as e:
                    print(f"⚠ Error disconnecting voice client: {e}")

            self.voice_client = None

            # Clear audio queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break

            print(f"✅ Cleaned up {count} voice connection(s)")
            await ctx.followup.send(f"✅ Cleaned up {count} voice connection(s). You can now use /connect_vc again.")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            await ctx.followup.send(f"✅ Cleanup attempted (with errors)", ephemeral=True)

    @discord.slash_command(name="disconnect_vc", description="Disconnect the bot from voice channel")
    async def leave_vc(self, ctx: discord.ApplicationContext):
        """Disconnect bot from voice channel"""
        await ctx.defer()

        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.followup.send("❌ Not connected to any voice channel", ephemeral=True)
            return

        try:
            channel_name = self.voice_client.channel.name
            print(f"🔌 Disconnecting from {channel_name}...")

            # Stop any playing audio
            if self.voice_client.is_playing():
                self.voice_client.stop()

            # Disconnect
            await self.voice_client.disconnect(force=True)
            self.voice_client = None

            # Clear audio queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break

            print(f"✅ Disconnected from {channel_name}")
            await ctx.followup.send(f"✅ Disconnected from {channel_name}")
        except Exception as e:
            print(f"❌ Error during disconnect: {e}")
            self.voice_client = None
            await ctx.followup.send(f"✅ Disconnected (with cleanup)", ephemeral=True)

    async def play_tts_audio(self, audio_data: bytes):
        """Add TTS audio to the playback queue"""
        if not self.voice_client or not self.voice_client.is_connected():
            print("⚠ Bot not connected to voice channel - cannot play audio")
            return

        await self.audio_queue.put(audio_data)
        print(f"🎵 Added audio to queue (queue size: {self.audio_queue.qsize()})")

    async def _audio_playback_task(self):
        """Background task to play audio from the queue"""
        self.is_playing = True
        print("🎵 Audio playback task started")

        while True:
            try:
                # Wait for audio data from queue
                audio_data = await self.audio_queue.get()

                if not self.voice_client or not self.voice_client.is_connected():
                    print("⚠ Voice client disconnected, stopping playback task")
                    break

                # Play the audio
                await self._play_audio(audio_data)

            except Exception as e:
                print(f"❌ Error in audio playback task: {e}")
                await asyncio.sleep(1)

        self.is_playing = False
        print("🎵 Audio playback task stopped")

    async def _play_audio(self, audio_data: bytes):
        """Play audio data in voice channel"""
        temp_file = None
        try:
            # Wait for current audio to finish
            while self.voice_client and self.voice_client.is_playing():
                await asyncio.sleep(0.1)

            if not self.voice_client or not self.voice_client.is_connected():
                print("⚠ Voice client disconnected during playback")
                return

            # Save audio to temporary file (FFmpeg works better with file path than pipe for mp3)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Create audio source from file
            audio_source = discord.FFmpegPCMAudio(temp_file_path)

            # Use an event to track when playback is done
            playback_done = asyncio.Event()

            def after_playback(error):
                if error:
                    print(f"❌ Playback error: {error}")
                else:
                    print("✓ Finished playing audio")

                # Clean up temp file
                try:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except Exception as e:
                    print(f"⚠ Failed to delete temp file: {e}")

                self.bot.loop.call_soon_threadsafe(playback_done.set)

            # Play the audio
            self.voice_client.play(audio_source, after=after_playback)
            print("🔊 Playing TTS audio")

            # Wait for playback to finish (with timeout)
            try:
                await asyncio.wait_for(playback_done.wait(), timeout=30.0)
            except asyncio.TimeoutError:
                print("⚠ Audio playback timeout")
                if self.voice_client and self.voice_client.is_playing():
                    self.voice_client.stop()
                # Clean up temp file on timeout
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            import traceback
            traceback.print_exc()
            # Clean up temp file on error
            if temp_file and hasattr(temp_file, 'name') and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass

    async def fetch_tts_from_backend(self, text: str, voice: str = "onyx") -> bytes:
        """Fetch TTS audio from backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.backend_url}/api/tts"
                payload = {"text": text, "voice": voice}

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        print(f"✓ Fetched TTS audio from backend ({len(audio_data)} bytes)")
                        return audio_data
                    else:
                        error = await response.text()
                        print(f"❌ Backend TTS error: {error}")
                        return None

        except Exception as e:
            print(f"❌ Error fetching TTS from backend: {e}")
            return None


def setup(bot):
    bot.add_cog(TextToSpeechCogCommands(bot))