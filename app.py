import discord
from bot.recievers.discord_rcvr import RadiantStarterClient
import os

intents = discord.Intents.default()
intents.message_content = True
client = RadiantStarterClient(intents=intents)
client.run(os.environ.get("DISCORD_API_TOKEN"))  # Ensure you set your Discord bot token in the environment variable DISCORD_TOKEN