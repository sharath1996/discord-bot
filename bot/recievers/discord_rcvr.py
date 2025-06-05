import discord
from discord import Message, TextChannel, Interaction
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import os
import dotenv
import json
# Load environment variables from .env file
dotenv.load_dotenv()

class GoalsAtNightModal(discord.ui.Modal, title="Submit your achievements"):
    
    goals = discord.ui.TextInput(label="What did you do today?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: Interaction):
        
        # Dump this to a json file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "timestamp": timestamp,
            "achievments": self.goals.value,
            "user": interaction.user.name,
        }

        with open('achievements.json', 'a') as f:
            json.dump(data, f, indent=4)
            
        
        await interaction.response.send_message(f"@{interaction.user.name} achievments are: {self.goals.value}", ephemeral=False)

class GoalsAtNightView(discord.ui.View):
    @discord.ui.button(label="Submit your achievements", style=discord.ButtonStyle.primary)
    async def submit_goals(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GoalsAtNightModal())

class GoalsAtMorningModal(discord.ui.Modal, title="Plan for today"):
    
    goals = discord.ui.TextInput(label="What are you planning do today?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: Interaction):
        
        # Dump this to a json file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "timestamp": timestamp,
            "goals": self.goals.value,
            "user": interaction.user.name,
        }

        with open('achievements.json', 'a') as f:
            json.dump(data, f, indent=4)
            
        
        await interaction.response.send_message("Your plans have been recorded!", ephemeral=True)

class GoalsAtMorningView(discord.ui.View):
    @discord.ui.button(label="Submit your plan", style=discord.ButtonStyle.primary)
    async def submit_goals(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GoalsAtNightModal())

class RadiantStarterClient(discord.Client):
    
    async def on_ready(self):
        print('Logged on as', self.user)
        # Schedule the daily message at 10 AM
        # await self.send_hello_message()

        scheduler = AsyncIOScheduler()
        # Replace CHANNEL_ID with your actual channel ID
        scheduler.add_job(self.send_daily_night_message, 'cron', hour=21, minute=33)
        scheduler.add_job(self.send_daily_morning_message, 'cron', hour=9, minute=0)  # For morning goals
        scheduler.start()


    async def send_hello_message(self):
        channel_id = os.environ.get("DISCORD_CHANNEL_ID")
        channel = self.get_channel(int(channel_id))
        if channel:
            await channel.send("Hello! I am Radiant Starter Bot. I will help you to plan your day and track your achievements.")
        else:
            print(f"Channel with ID {channel_id} not found.")

    
    async def send_daily_night_message(self):
        channel_id = os.environ.get("DISCORD_CHANNEL_ID")
        channel = self.get_channel(int(channel_id))
        if channel:
            await channel.send("Click the button below to submit your achievements for today:",
                view=GoalsAtNightView()
            )
        else:
            print(f"Channel with ID {channel_id} not found.")
    
    
    async def send_daily_morning_message(self):
        channel_id = os.environ.get("DISCORD_CHANNEL_ID")
        channel = self.get_channel(int(channel_id))
        if channel:
            await channel.send(
                "Click the button below to submit your plan for today:",
                view=GoalsAtMorningView()
            )
        else:
            print(f"Channel with ID {channel_id} not found.")

    
    async def on_message(self, message:Message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        local_obj_channel:TextChannel = message.channel

        if message.content.startswith('!workout'):
            await local_obj_channel.send("In future, I will help you to plan your workout sessions. For now, Sorry!.")  


    # on command handler
