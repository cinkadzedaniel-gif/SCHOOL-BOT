from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard.inline import dedline_keyboard, main_keyboard 
from database import add_dedline, get_dedlines
from google_service import create_event, CALENDAR_ID

dedline_router = Router()

class Dedline(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_description = State()

@dedline_router.message(F.text == "Дедлайни")
async def menu(message: Message):
    await message.answer("Оберіть дію", reply_markup=dedline_keyboard())

@dedline_router.message(F.text == "Додати дедлайн")
async def add_dedlina(message: Message, state: FSMContext):
    await message.answer("Напишіть назву дедлайну")
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
    await message.answer("Введіть опис дедлайна")
    await state.set_state(Dedline.waiting_for_description)

@dedline_router.message(Dedline.waiting_for_description)
async def waiting_discription(message: Message, state: FSMContext):
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
        f"📝 Опис: {discription}"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard())

@dedline_router.message(F.text == "Переглянути дедлайни")
async def view_dedline(message: Message):
    user_id = message.from_user.id
    deadlines = await get_dedlines(user_id)

    if not deadlines:
        await message.answer(
            "📭 **У вас немає активних дедлайнів.**",
            parse_mode="Markdown",
        )
        return

    text = "📂 **ВАШІ ДЕДЛАЙНИ:**\n━━━━━━━━━━━━━━━━━━━\n\n"
    
    for index, item in enumerate(deadlines, start=1):
        text += f"{index}. 📌 **Завдання:** {item['title']}\n⏳ **До:** {item['deadline_date']}\n📝 **Опис:** {item['description']}\n\n"

    await message.answer(text, parse_mode="Markdown")