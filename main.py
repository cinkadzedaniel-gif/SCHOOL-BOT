import asyncio
import aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,    
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from bot import scheduler
from dotenv import load_dotenv 
import os
from handlers.navigation import back_router
from handlers.grades import grades_router
from handlers.homework import homework_router
from handlers.schedu import schedule_router
from handlers.schedulerr import scheduler_router
from handlers.start import start_router
from bot import bot
from database import init_db


dp = Dispatcher()



dp.include_router(back_router)
dp.include_router(grades_router)
dp.include_router(homework_router)
dp.include_router(scheduler_router)
dp.include_router(schedule_router)
dp.include_router(start_router)






# --- ЗАПУСК ---
async def main():
    print("🚀 БОТ УСПІШНО ЗАПУСТИВСЯ!")
    await init_db()
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())