"""
Backend connection event handler
Starts WebSocket connection to backend when bot is ready
"""
import discord
from discord.ext import commands
import sys
import os

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.websocket_client import BackendWebSocketClient


class BackendConnectionEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ws_client = BackendWebSocketClient(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        """Start WebSocket connection when bot is ready"""
        print("🤖 Bot is ready, connecting to backend WebSocket...")

        # Start WebSocket client in background
        self.bot.loop.create_task(self.ws_client.start())


def setup(bot):
    bot.add_cog(BackendConnectionEvents(bot))
