import discord
from discord import Message, TextChannel, Interaction
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import asyncio
import os

class GoalsModal(discord.ui.Modal, title="Submit Your Goals"):
    goals = discord.ui.TextInput(label="Your goals:", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: Interaction):
        # Write the user's goals to a file
        with open("user_goals.txt", "a", encoding="utf-8") as f:
            f.write(f"{interaction.user}: {self.goals.value}\n")
        await interaction.response.send_message("Your goals have been recorded!", ephemeral=True)

class GoalsView(discord.ui.View):
    @discord.ui.button(label="Submit your goals", style=discord.ButtonStyle.primary)
    async def submit_goals(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GoalsModal())

class MyClient(discord.Client):
    
    async def on_ready(self):
        print('Logged on as', self.user)
        # Schedule the daily message at 10 AM
        scheduler = AsyncIOScheduler()
        # Replace CHANNEL_ID with your actual channel ID
        scheduler.add_job(self.send_daily_message, 'cron', hour=16, minute=30)
        scheduler.start()

    async def send_daily_message(self):
        channel_id = os.get("channelID")  # <-- Replace with your channel ID (as an int)
        channel = self.get_channel(channel_id)
        if channel:
            await channel.send(
                "Click the button below to submit your goals for today:",
                view=GoalsView()
            )
        else:
            print(f"Channel with ID {channel_id} not found.")

    async def on_message(self, message:Message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        local_obj_channel:TextChannel = message.channel
        if message.content.startswith('!goals'):
            await local_obj_channel.send(
                "Click the button below to submit your goals for today:",
                view=GoalsView()
            )

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(os.environ.get("DISCORD_TOKEN"))  # Ensure you set your Discord bot token in the environment variable DISCORD_TOKEN