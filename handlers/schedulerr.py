from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
import aiosqlite
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard.inline import main_keyboard, scheduler_keyboard
import asyncio
from datetime import datetime, timedelta
from database import init_db, get_remimbers, RB_NAME
from bot import bot 
from bot import scheduler  

scheduler_router = Router()

class Scheduler(StatesGroup):
    waiting_for_time = State()
    waiting_for_text = State()

@scheduler_router.message(F.text == "⏲Нагадування")
async def menu_scheduler(message: Message):
    await message.answer("Оберіть дію з нагадуваннями", reply_markup=scheduler_keyboard())

@scheduler_router.message(F.text == "Встановити нагадування")
async def start_scheduler(message: Message, state: FSMContext):
    await state.set_state(Scheduler.waiting_for_time)
    await message.answer("Напишіть час у хвилинах через який прийде одноразове нагадування:", reply_markup=ReplyKeyboardRemove())

# Виправлене скасування для будь-якого етапу нагадувань
@scheduler_router.message(Scheduler.waiting_for_time, F.text == "❌ Скасувати")
@scheduler_router.message(Scheduler.waiting_for_text, F.text == "❌ Скасувати")
@scheduler_router.message(F.text == "❌ Скасувати")
async def cancel_scheduler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Додавання нагадування скасовано.", reply_markup=main_keyboard()) 

@scheduler_router.message(Scheduler.waiting_for_time)
async def waiting_time(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await cancel_scheduler(message, state)
        return

    try:
        minutes = int(message.text)
        if minutes <= 0:
            await message.answer("Введіть число більше за 0:")
            return
    except ValueError:
        await message.answer("Будь ласка, введіть число (кількість хвилин):")
        return

    await state.update_data(time=minutes)
    await state.set_state(Scheduler.waiting_for_text)
    await message.answer("Введіть який текст буде приходити вам коли прозвучить нагадування:")

@scheduler_router.message(Scheduler.waiting_for_text)
async def waiting_text(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await cancel_scheduler(message, state)
        return

    text = message.text
    user_data = await state.get_data()
    minutes = user_data.get("time", 10)

    run_date = datetime.now() + timedelta(minutes=minutes)

    scheduler.add_job(
        send_remimber_job,
        trigger='date',
        run_date=run_date,
        kwargs={"chat_id": message.chat.id, "text": text},
        misfire_grace_time=60
    )

    user_id = message.from_user.id

    async with aiosqlite.connect(RB_NAME) as rb:
        await rb.execute('''
        INSERT INTO remimbers (user_id, text, run_time)       
        VALUES (?, ?, ?)
        ''', (user_id, text, str(minutes)))
        await rb.commit()

    await state.clear()

    text_for_user = (
        "✅ **Нагадування додано!**\n" 
        f"⏰ **Час:** {minutes} хв.\n"
        f"📝 **Текст:** {text}\n"
    )
    await message.answer(text_for_user, reply_markup=main_keyboard(), parse_mode="Markdown")

async def send_remimber_job(chat_id: int, text: str):
    try:
        await bot.send_message(
            chat_id=chat_id, text=f"⏰ **НАГАДУВАННЯ!**\n\n📌 {text}", parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Помилка надсилання нагадування: {e}")

@scheduler_router.message(F.text == "Переглянути наявні нагадування")
async def show_reminders(message: Message):
    user_id = message.from_user.id
    reminders = await get_remimbers(user_id)

    if not reminders:
        await message.answer(
            "📭 **У вас немає активних нагадувань.**",
            parse_mode="Markdown",
        )
        return

    text = "⏰ **ВАШІ НАГАДУВАННЯ:**\n━━━━━━━━━━━━━━━━━━━\n\n"
    
    if isinstance(reminders, dict):
        text += f"📌 **Текст:** {reminders['text']}\n⏳ **Через скільки хв:** {reminders['run_time']}\n\n"
    elif isinstance(reminders, list):
        for rem in reminders:
            text += f"📌 **Текст:** {rem['text']}\n⏳ **Через скільки хв:** {rem['run_time']}\n\n"

    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard())