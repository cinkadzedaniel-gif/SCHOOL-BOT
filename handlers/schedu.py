from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from datetime import datetime, timedelta
import time


schedule_router = Router()



SCHEDULE = {
    0: [
        "1. 📐 Алгебра",
        "2. 🧲 Фізика",
        "3. 🇺🇦 Українська мова",
        "4. 🏛 Історія",
        "5. 🇬🇧 Англійська мова",
    ],
    1: [
        "1. 📏 Геометрія",
        "2. 🌿 Біологія",
        "3. 🧪 Хімія",
        "4. 📖 Література",
        "5. ⚽ Фізкультура",
    ],
    2: [
        "1. 💻 Інформатика",
        "2. 📐 Алгебра",
        "3. 🌍 Географія",
        "4. 🏛 Історія",
        "5. 🧲 Фізика",
    ],
    3: [
        "1. 🇺🇦 Українська мова",
        "2. 🇬🇧 Англійська мова",
        "3. 📏 Геометрія",
        "4. 🧪 Хімія",
        "5. 🎨 Образотворче мист.",
    ],
    4: [
        "1. 📐 Алгебра",
        "2. 🌿 Біологія",
        "3. 📖 Література",
        "4. ⚽ Фізкультура",
    ],
    5: ["🥳 Вихідний! Уроків немає 🎉"],
    6: ["🥳 Вихідний! Уроків немає 🎉"],
}

DAYS_UA = [
    "Понеділок",
    "Вівторок",
    "Середа",
    "Четвер",
    "П'ятниця",
    "Субота",
    "Неділя",
]





# --- МЕНЮ РОЗКЛАДУ ---
@schedule_router.message(F.text == "📅 Розклад")
async def btn_schudle(message: Message):
    kb_schoudle = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Розклад на сьогодні")],
            [KeyboardButton(text="🚀 Розклад на завтра")],
            [KeyboardButton(text="🗓 Розклад на тиждень")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "🔎 Оберіть, який саме розклад хочете переглянути:",
        reply_markup=kb_schoudle,
    )


@schedule_router.message(F.text == "📌 Розклад на сьогодні")
async def schoulde_today(message: Message):
    today_num = datetime.now().weekday()
    day_name = DAYS_UA[today_num]
    lessons = "\n".join(SCHEDULE[today_num])

    await message.answer(
        f"📌 **Розклад на сьогодні ({day_name}):**\n\n{lessons}",
        parse_mode="Markdown",
    )


@schedule_router.message(F.text == "🚀 Розклад на завтра")
async def schoulde_tomorrow(message: Message):
    tomorrow_num = (datetime.now() + timedelta(days=1)).weekday()
    day_name = DAYS_UA[tomorrow_num]
    lessons = "\n".join(SCHEDULE[tomorrow_num])

    await message.answer(
        f"🚀 **Розклад на завтра ({day_name}):**\n\n{lessons}",
        parse_mode="Markdown",
    )


@schedule_router.message(F.text == "🗓 Розклад на тиждень")
async def schoulde_onweek(message: Message):
    text = "📅 **РОЗКЛАД НА ВЕСЬ ТИЖДЕНЬ**\n━━━━━━━━━━━━━━━━━━━\n\n"

    for day_num in range(5):
        day_name = DAYS_UA[day_num]
        lessons = "\n".join(SCHEDULE[day_num])
        text += f"🔹 **{day_name}:**\n{lessons}\n\n"

    await message.answer(text, parse_mode="Markdown")
