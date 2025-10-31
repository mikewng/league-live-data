import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import config

# Python 3.13 compatibility fix for Windows voice
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = discord.Bot(intents=intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')

for filename in os.listdir('./events'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'events.{filename[:-3]}')

@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f"Bot online as the user: {bot.user}")

bot.run(TOKEN)