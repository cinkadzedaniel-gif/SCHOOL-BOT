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



def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Перевірка оцінок")],
            [KeyboardButton(text="📚 Домашнє завдання")],
            [KeyboardButton(text="📅 Розклад")],
            [KeyboardButton(text= "⏲Нагадування")],
            [KeyboardButton(text= "Дедлайни")],
            [KeyboardButton(text="Відмітитись для їдальні")]
        ],
        resize_keyboard=True,
    )


def subject_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📐 Алгебра"),
                KeyboardButton(text="📏 Геометрія"),
            ],
            [
                KeyboardButton(text="🇺🇦 Українська мова"),
                KeyboardButton(text="📖 Укр. література"),
            ],
            [
                KeyboardButton(text="🌍 Зарубіжна література"),
                KeyboardButton(text="🇬🇧 Англійська мова"),
            ],
            [
                KeyboardButton(text="🧲 Фізика"),
                KeyboardButton(text="🧪 Хімія"),
            ],
            [
                KeyboardButton(text="🌿 Біологія"),
                KeyboardButton(text="🗺 Географія"),
            ],
            [
                KeyboardButton(text="🏛 Історія України"),
                KeyboardButton(text="📜 Всесвітня історія"),
            ],
            [
                KeyboardButton(text="💻 Інформатика"),
                KeyboardButton(text="🎨 Мистецтво"),
            ],
            [
                KeyboardButton(text="🛡 ЗБД"),
                KeyboardButton(text="⚖️ Громадянська освіта"),
            ],
            [KeyboardButton(text="❌ Скасувати")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def dedline_dates_keyboard():
    days_ua = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    today = datetime.now()
    keyboard_buttons = []
    row = []

    for i in range(1, 6):
        future_day = today + timedelta(days=i)
        day_name = days_ua[future_day.weekday()]
        day_str = future_day.strftime("%d.%m")

        btn_text = f"📅 {day_name} ({day_str})"
        row.append(KeyboardButton(text=btn_text))

        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []

    if row:
        keyboard_buttons.append(row)

    keyboard_buttons.append([KeyboardButton(text="❌ Скасувати")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def scheduler_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text = "Встановити нагадування")],
            [KeyboardButton(text="Переглянути наявні нагадування")],
            [KeyboardButton(text = "Вимкнути нагадування")],
            [KeyboardButton(text = "❌ Скасувати")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True

    )


def dedline_keyboard():
    return ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text = "Додати дедлайн")],
            [KeyboardButton(text = "Переглянути дедлайни")],
            [KeyboardButton(text = "❌ Скасувати")]
        ]
    )