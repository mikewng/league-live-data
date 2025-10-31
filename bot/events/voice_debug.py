"""
Voice state debugging event handler
"""
import discord
from discord.ext import commands
import traceback


class VoiceDebugEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Track voice state changes for debugging"""
        # Only log bot's own voice state changes
        if member.id == self.bot.user.id:
            if before.channel != after.channel:
                if after.channel is None:
                    print(f"🔴 Bot left voice channel: {before.channel.name if before.channel else 'Unknown'}")
                    print(f"   Reason: Voice state changed, channel is now None")
                    # Print stack trace to see what caused the disconnect
                    print("   Call stack:")
                    traceback.print_stack()
                elif before.channel is None:
                    print(f"🟢 Bot joined voice channel: {after.channel.name}")
                else:
                    print(f"🔄 Bot moved from {before.channel.name} to {after.channel.name}")


def setup(bot):
    bot.add_cog(VoiceDebugEvents(bot))
