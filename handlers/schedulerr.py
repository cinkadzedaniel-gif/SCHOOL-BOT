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

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import scheduler  


scheduler_router = Router()


class Scheduler(StatesGroup):
    waiting_for_time = State()
    waitinfg_for_text = State()





@scheduler_router.message(F.text == "⏲Нагадування")
async def menu_scheduler(message:Message ):
    await message.answer("Оберіть дію з нагадуваннями", reply_markup = scheduler_keyboard())



@scheduler_router.message(F.text == "Встановити нагадування")
async def start_scheduler(message:Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "❌ Додавання нагадування скасовано.", reply_markup=main_keyboard()
        )
        return 

    await state.set_state(Scheduler.waiting_for_time)
    await message.answer("Напишіть час у хвилинах через який прийде одноразове нагадування:")



async def send_remimber_job(chat_id:int, text: str):
    await bot.send_message(
        chat_id=chat_id, text =f"⏰ **НАГАДУВАННЯ!**\n\n📌 {text}", parse_mode = "Markdown"
    )


    SCHEDULER_LIST = [item for item in SCHEDULER_LIST if item.get("id")]


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
    
    # Якщо повертається один словник або список
    if isinstance(reminders, dict):
        text += f"📌 **Текст:** {reminders['text']}\n⏳ **Через скільки хв:** {reminders['run_time']}\n\n"
    elif isinstance(reminders, list):
        for rem in reminders:
            text += f"📌 **Текст:** {rem['text']}\n⏳ **Через скільки хв:** {rem['run_time']}\n\n"

    await message.answer(text, parse_mode="Markdown")


@scheduler_router.message(Scheduler.waitinfg_for_text, F.text == "❌ Скасувати")
async def cancel_scheduler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Додавання нагадування скасовано.", reply_markup=main_keyboard()
    )


@scheduler_router.message(Scheduler.waiting_for_time)
async def waitig_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(Scheduler.waitinfg_for_text)
    await message.answer("Введіть який текст буде приходити вам коли прозвучить нагадування")


@scheduler_router.message(Scheduler.waitinfg_for_text)
async def waiting_text(message: Message, state: FSMContext):

    try:
        user_num = float(message.text)  # Спробуємо перетворити текст на число
        if user_num < 1:
            await message.answer("Введіть число, яке більше або дорівнює 1")
            return  
    except ValueError:
    # Якщо це взагалі не число (наприклад, літери)
        await message.answer("Будь ласка, введіть коректне число")
        return

    await state.update_data(scheduler_text=message.text)

    user_data = await state.get_data()
    run_time = user_data.get("time")
    text = user_data.get("scheduler_text")

    try:
        minutes = int(run_time)
    except ValueError:
        minutes = 10

    run_date = datetime.now() + timedelta(minutes=minutes)

    scheduler.add_job(
        send_remimber_job,
        trigger='date',
        run_date=run_date,
        kwargs={"chat_id": message.chat.id, "text": text}
    )

    user_id = message.from_user.id

    async with aiosqlite.connect(RB_NAME) as rb:
        await rb.execute('''
        INSERT INTO remimbers (user_id, text, run_time)       
        VALUES (?, ?, ?)
        ''', (user_id, text, str(run_time)))
        await rb.commit()

    await state.clear()

    text_for_user = (
        "✅ **Нагадування додано!**\n" 
        f"⏰ **Час:** {run_time} хв.\n"
        f"📝 **Текст:** {text}\n"
    )
    await message.answer(text_for_user, reply_markup=main_keyboard(), parse_mode="Markdown")