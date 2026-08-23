# bot.py
import os
from dotenv import load_dotenv
from aiogram import Bot
from apscheduler.jobstores.memory import MemoryJobStore
import pytz

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)



# scheduler_instance.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

timezone = pytz.timezone("Europe/Kiev")
scheduler = AsyncIOScheduler(timezone=timezone)