from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.types import Message
from keyboard.inline import subject_keyboard,main_keyboard
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from database import init_db, save_grades, get_user_subject_grades

grades_router = Router()


class Calculate(StatesGroup):
    waiting_for_subject = State()
    waiting_for_grades = State()





# --- МЕНЮ ОЦІНОК ---
@grades_router.message(F.text == "📊 Перевірка оцінок")
async def start_calc(message: Message, state: FSMContext):
    await state.set_state(Calculate.waiting_for_subject)

    await message.answer(
        "📊 **Калькулятор оцінок**\n\n"
        "Оберіть предмет, для якого хочете додати або переглянути оцінки:",
        reply_markup=subject_keyboard(),
        parse_mode="Markdown",
    )


@grades_router.message(Calculate.waiting_for_subject)
async def proces_calc_subjet(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "❌ Розрахунок скасовано.", reply_markup=main_keyboard()
        )
        return

    subject = message.text
    user_id = message.from_user.id

    await state.update_data(subject=subject)
    await state.set_state(Calculate.waiting_for_grades)

    # Отримуємо поточні оцінки з бази даних замість словника
    current_grades_str = await get_user_subject_grades(user_id, subject)
    
    if current_grades_str:
        current_str = current_grades_str
    else:
        current_str = "немає"

    kb_cancel = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Скасувати")]], resize_keyboard=True
    )
    await message.answer(
        f"📚 Предмет: **{subject}**\n"
        f"📌 Поточні оцінки: `{current_str}`\n\n"
        f"✍️ Введіть нові оцінки через пробіл (наприклад: `10 11 9`):",
        parse_mode="Markdown",
        reply_markup=kb_cancel,
    )

@grades_router.message(Calculate.waiting_for_grades)
async def process_calc_grades(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer("❌ Розрахунок скасовано.", reply_markup=main_keyboard())
        return

    user_data = await state.get_data()
    subject = user_data.get("subject")
    user_id = message.from_user.id

    # Парсинг оцінок
    raw_input = message.text.replace(",", " ").split()
    new_grades = [int(i) for i in raw_input if i.isdigit() and 1 <= int(i) <= 12]

    if not new_grades:
        await message.answer("⚠️ Введіть коректні оцінки від 1 до 12.")
        return

    # Зберігаємо в базу даних
    new_grades_str = ", ".join(map(str, new_grades))
    await save_grades(user_id, subject, new_grades_str)

    # Отримуємо оновлений список для розрахунку
    full_grades_str = await get_user_subject_grades(user_id, subject)
    grades_list = [int(i) for i in full_grades_str.replace(",", " ").split()]
    
    # Розрахунок середнього бала
    avg = sum(grades_list) / len(grades_list)

    await state.clear()

    await message.answer(
        f"✅ Оцінки з **{subject}** збережено!\n"
        f"📝 Усі оцінки: `{', '.join(map(str, grades_list))}`\n"
        f"📈 Середній бал: `{avg:.2f}`",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )