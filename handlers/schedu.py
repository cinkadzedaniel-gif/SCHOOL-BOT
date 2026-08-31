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
        "1. ⚽ Фіз-ра",
        "2. 🇺🇦 Укр.мова (каб. 20)",
        "3. 🇬🇧 Англ.мова (каб. 21)",
        "4. 📐 Алгебра (каб. 18)",
        "5. 🌿 Біологія (каб. 14)",
        "6. 🏛 Історія України (каб. 5)",
        "7. 🎨 Образотворче мистецтво (каб. 19)",
    ],
    1: [
        "1. 🇬🇧 Англ.мова (каб. 21)",
        "2. 📖 Укр. літ. (каб. 20)",
        "3. 🧲 Фізика (каб. 22)",
        "4. 🛠 Технології майстерня",
        "5. 🌿 Біологія (каб. 14)",
        "6. 🎵 Музичне мистецтво (укриття)",
        "7. 📏 Геометрія (каб. 18)",
        "8. 💻 Інформатика (II група)",
    ],
    2: [
        "1. ⚽ Фіз-ра",
        "2. 🌿 Біологія (каб. 14)",
        "3. 🏛 Історія України (каб. 5)",
        "4. 📐 Алгебра (каб. 18)",
        "5. 🇺🇦 Укр.мова (каб. 20)",
        "6. 📖 Зар. літ. (каб. 19)",
        "7. 🛡 ЗБД (каб. 22)",
    ],
    3: [
        "2. 🇬🇧 Англ.мова (каб. 21)",
        "3. 🧪 Хімія (каб. 14)",
        "4. 🧲 Фізика (каб. 22)",
        "5. 🏛 Всесвітня історія (каб. 5)",
        "6. 🌍 Географія (каб. 22)",
        "7. 🇺🇦 Укр.мова (каб. 20)",
        "8. 📏 Геометрія (каб. 18)",
    ],
    4: [
        "1. 🌍 Географія (каб. 22)",
        "2. ⚽ Фіз-ра",
        "3. 📐 Алгебра (каб. 18)",
        "4. 🇺🇦 Укр.мова (каб. 20)",
        "5. 📖 Укр. літ. (каб. 20)",
        "6. 🌿 Біологія (каб. 14)",
        "7. 💻 Інформатика (II група)",
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
