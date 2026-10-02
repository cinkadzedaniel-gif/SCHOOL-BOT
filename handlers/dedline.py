from datetime import datetime
import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from keyboard.inline import dedline_keyboard, main_keyboard 
from database import add_dedline, get_dedlines, delete_deadline_from_db
from google_service import create_event, delete_event, CALENDAR_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Завантажуємо змінні середовища для отримання ID каналу
load_dotenv()
CHANNEL_ID = os.getenv("CHANNEL_ID")

dedline_router = Router()

class Dedline(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_description = State()

# Глобальне скасування для будь-якого стану дедлайнів
@dedline_router.message(Dedline.waiting_for_name, F.text == "❌ Скасувати")
@dedline_router.message(Dedline.waiting_for_date, F.text == "❌ Скасувати")
@dedline_router.message(Dedline.waiting_for_description, F.text == "❌ Скасувати")
@dedline_router.message(F.text == "❌ Скасувати")
async def cancel_deadline(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Дюдію скасовано. Повертаємось у головне меню", reply_markup=main_keyboard())

@dedline_router.message(F.text == "Посилання")
async def menu(message: Message):
    await message.answer("Оберіть дію", reply_markup=dedline_keyboard())

@dedline_router.message(F.text == "Додати посилання")
async def add_dedlina(message: Message, state: FSMContext):
    await message.answer("Напишіть назву дедлайну", reply_markup=dedline_keyboard())
    await state.set_state(Dedline.waiting_for_name)

@dedline_router.message(Dedline.waiting_for_name)
async def waiting_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Чудово, тепер напишіть дату та час у форматі **РРРР-ММ-ДД ГГ:ХХ**\n(Наприклад: `2026-09-01 15:00`):", parse_mode="Markdown")
    await state.set_state(Dedline.waiting_for_date)

@dedline_router.message(Dedline.waiting_for_date)
async def waiting_data(message: Message, state: FSMContext):
    date_text = message.text
    try:
        datetime.strptime(date_text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("❌ Неправильний формат! Введіть у форматі **РРРР-ММ-ДД ГГ:ХХ** (наприклад: `2026-09-01 15:00`):", parse_mode="Markdown")
        return

    await state.update_data(date=date_text)
    await message.answer("Введіть посилання на урок")
    await state.set_state(Dedline.waiting_for_description)

@dedline_router.message(Dedline.waiting_for_description)
async def waiting_discription(message: Message, state: FSMContext, bot: Bot):
    discription = message.text

    user_data = await state.get_data()
    title = user_data.get("name")
    date_str = user_data.get("date")
    user_id = message.from_user.id

    event_id = None
    try:
        start_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        event_id = create_event(
            calendar_id=CALENDAR_ID,
            summary=f"Дедлайн: {title}",
            description=discription,
            start_time=start_time,
            duration_minutes=60
        )
    except Exception as e:
        print(f"Помилка створення події в Google Календарі: {e}")

    await add_dedline(title, date_str, discription, user_id, event_id)
    await state.clear()

    text = (
        "ДЕДЛАЙН ВСТАНОВЛЕНО ТА СИНХРОНІЗОВАНО З КАЛЕНДАРЕМ! 🚀\n"
        f"📌 Назва: {title}\n"
        f"⏳ Дата: {date_str}\n"
        f"📝 Посилання / Опис: {discription}"
    )

    # Відправляємо оновлену інформацію в канал
    try:
        if CHANNEL_ID:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📌 **Нове посилання / дедлайн!**\n\n{text}",
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Помилка при відправці в канал: {e}")

    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard())

@dedline_router.message(F.text == "Переглянути посилання")
async def view_dedline(message: Message):
    user_id = message.from_user.id
    deadlines = await get_dedlines(user_id)

    if not deadlines:
        await message.answer("📭 **У вас немає активних дедлайнів.**", parse_mode="Markdown")
        return

    for item in deadlines:
        text = (
            f"📌 **Назва:** {item['title']}\n"
            f"⏳ **Дата:** {item['deadline_date']}\n"
            f"📝 **Опис:** {item['description']}"
        )
        await message.answer(text, parse_mode="Markdown")

@dedline_router.callback_query(F.data.startswith("del_deadline_"))
async def process_delete_deadline(callback: CallbackQuery):
    deadline_id = int(callback.data.split("_")[2])
    calendar_event_id = await delete_deadline_from_db(deadline_id)

    if calendar_event_id:
        try:
            delete_event(CALENDAR_ID, calendar_event_id)
        except Exception as e:
            print(f"Помилка видалення з календаря: {e}")

    await callback.message.edit_text("🗑 **Дедлайн успішно видалено!**", parse_mode="Markdown")
    await callback.answer()