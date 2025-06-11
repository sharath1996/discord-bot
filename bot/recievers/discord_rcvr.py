import discord
from discord import Message, TextChannel
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import dotenv
import openai
from abc import ABC, abstractmethod
import json
import datetime
# Load environment variables from .env file
dotenv.load_dotenv()

# --- Interface for Greeting Generation (Single Responsibility, Open/Closed) ---
class IGreetingGenerator(ABC):
    @abstractmethod
    def generate_greeting(self) -> str:
        pass

# --- Concrete Greeting Generators ---
class MorningGreetingGenerator(IGreetingGenerator):
    def generate_greeting(self) -> str:
        openai.api_key = os.environ['OPENAI_API_KEY']
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates sweet and interesting morning greetings."},
                {"role": "user", "content": (
                    "Generate a sweet and interesting morning greeting for my loved one. "
                    "That message should include the reminder to plan the day and important tasks to them. "
                    "Your response should only be the greeting and do not include any other conversational elements. "
                    "There shall be no placeholders in the response, just the complete greeting text."
                )}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()

class NightGreetingGenerator(IGreetingGenerator):
    def generate_greeting(self) -> str:
        openai.api_key = os.environ['OPENAI_API_KEY']
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates sweet and interesting night greetings."},
                {"role": "user", "content": (
                    "Generate a sweet and interesting night greeting for my loved one. "
                    "That message should include the reminder to submit the achievements of the day and what are the important tasks that have already been done. "
                    "Your response should only be the greeting and do not include any other conversational elements. "
                    "There shall be no placeholders in the response, just the complete greeting text."
                )}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()

class WorkOutGenerator:

    def get_work_out_of_the_day(self) -> str:

        with open("workout.json", "r") as file:
            workout_data = json.load(file)
        
        # current day of the week in integer format (0=Monday, 6=Sunday)
        current_day = datetime.datetime.now().weekday() +1

        # Get the workout for the current day
        local_dict_workOut = workout_data.get(str(current_day), "No workout planned for today.")
        if local_dict_workOut == "No workout planned for today.":
            return local_dict_workOut
        local_str_workout = f"Today you can work on {local_dict_workOut['title']} \n {"\n".join(local_dict_workOut['workouts'])}"

        return local_str_workout

# --- Channel Service (Single Responsibility) ---
class ChannelService:
    
    def __init__(self, client: discord.Client):
        self.client = client

    def get_channel(self) -> TextChannel:
        
        channel_id = os.environ.get("DISCORD_CHANNEL_ID")
        
        if not channel_id:
            raise ValueError("DISCORD_CHANNEL_ID not set in environment variables.")
        channel = self.client.get_channel(int(channel_id))
        
        if not channel:
            raise ValueError(f"Channel with ID {channel_id} not found.")
        
        return channel

# --- Scheduler Service (Single Responsibility, Dependency Inversion) ---
class SchedulerService:
    
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    def schedule_job(self, func, hour: int, minute: int, job_name: str):
        self.scheduler.add_job(func, 'cron', hour=hour, minute=minute, misfire_grace_time=60, id=job_name)

    def start(self):
        self.scheduler.start()

# --- Main Discord Bot Client (Single Responsibility, Liskov Substitution) ---
class RadiantStarterClient(discord.Client):
    
    def __init__(self, intents: discord.Intents = discord.Intents.default()):
        
        super().__init__(intents=intents)

        self._obj_channel = ChannelService(self)
        self._obj_scheduler = SchedulerService(AsyncIOScheduler())

    async def on_ready(self):
        self._obj_scheduler.schedule_job(self.send_daily_night_message, hour=21, minute=30, job_name="night_message")
        self._obj_scheduler.schedule_job(self.send_daily_morning_message, hour=6, minute=0, job_name="morning_message")
        # self._obj_scheduler.schedule_job(self.send_workout_message, hour=6, minute=30, job_name="workout_message")
        self._obj_scheduler.start()

    async def send_hello_message(self):
        try:
            channel = self._obj_channel.get_channel()
            await channel.send("Hello! I am Radiant Starter Bot. I will help you to plan your day and track your achievements.")
        except Exception as e:
            print(str(e))
            
    async def send_daily_night_message(self):
        try:
            channel = self._obj_channel.get_channel()
            nightGreetingGenerator = NightGreetingGenerator()
            night_greeting = nightGreetingGenerator.generate_greeting()
            await channel.send(night_greeting)
        except Exception as e:
            print(str(e))

    async def send_daily_morning_message(self):
        try:
            channel = self._obj_channel.get_channel()
            morningGreetingGenerator = MorningGreetingGenerator()
            morning_greeting = morningGreetingGenerator.generate_greeting()
            await channel.send(morning_greeting)
        except Exception as e:
            print(str(e))

    async def on_message(self, message: Message):
        
        if message.author == self.user:
            return
        
        if message.content.startswith('!workout'):
            
            workout_generator = WorkOutGenerator()
            workout_message = workout_generator.get_work_out_of_the_day()
            workout_message = f"Hey @{message.author.name}, \n{workout_message}"
            await message.channel.send(workout_message)
            
    @app_commands.command(name="workout", description="Get workout of the day")
    async def workout_command(self, interaction: discord.Interaction):
        workout_generator = WorkOutGenerator()
        workout_message = workout_generator.get_work_out_of_the_day()
        await interaction.response.send_message(workout_message)

    
