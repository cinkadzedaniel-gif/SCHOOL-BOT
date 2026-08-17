from aiogram.filters import Command, CommandStart
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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard.inline import subject_keyboard, main_keyboard, dedline_keyboard
import aiosqlite
from database import HM_NAME, get_homework


homework_router = Router()


class AddHomework(StatesGroup):
    waiting_for_subject = State()
    waiting_for_task = State()
    waiting_for_dedline = State()


@homework_router.message(F.text == "📚 Домашнє завдання")
async def hw_menu(message: Message):
    kb_hw = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати ДЗ")],
            [KeyboardButton(text="📋 Переглянути ДЗ")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "📝 Оберіть дію з домашнім завданням:", reply_markup=kb_hw
    )




@homework_router.message(F.text == "➕ Додати ДЗ")
async def start_add_hw(message: Message, state: FSMContext):
    await state.set_state(AddHomework.waiting_for_subject)
    await message.answer(
        "📚 Оберіть предмет зі списку або введіть його назву вручну:",
        reply_markup=subject_keyboard(),
    )


@homework_router.message(AddHomework.waiting_for_subject)
async def process_subject(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "❌ Додавання ДЗ скасовано.", reply_markup=main_keyboard()
        )
        return

    await state.update_data(subject=message.text)
    await state.set_state(AddHomework.waiting_for_task)
    await message.answer(
        f"✅ Обрано предмет: **{message.text}**\n\n✍️ Тепер введіть текст завдання:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


@homework_router.message(AddHomework.waiting_for_task)
async def process_task(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "❌ Додавання ДЗ скасовано.", reply_markup=main_keyboard()
        )
        return

    await state.update_data(task=message.text)
    await state.set_state(AddHomework.waiting_for_dedline)
    await message.answer(
        "⏰ Оберіть дедлайн зі списку або введіть дату вручну:",
        reply_markup=dedline_keyboard(),
    )


@homework_router.message(AddHomework.waiting_for_dedline)
async def process_dedline(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await message.answer(
            "❌ Додавання ДЗ скасовано.", reply_markup=main_keyboard()
        )
        return

    await state.update_data(dedline=message.text)

    user_data = await state.get_data()
    subject = user_data.get("subject")
    task = user_data.get("task")
    dedline = user_data.get("dedline")

    user_id = message.from_user.id

    async with aiosqlite.connect(HM_NAME) as db:
        await db.execute('''
        INSERT INTO homework (user_id, subject, task, dedline)       
        VALUES (?, ?, ?, ?)

        ''', (user_id, subject,task,dedline))
        await db.commit()

    await state.clear()

    text = (
        f"✅ **Домашнє завдання успішно додано!**\n\n"
        f"📚 **Предмет:** {subject}\n"
        f"📝 **Завдання:** {task}\n"
        f"⏰ **Дедлайн:** {dedline}"
    )

    await message.answer(
        text, parse_mode="Markdown", reply_markup=main_keyboard()
    )


@homework_router.message(F.text == "📋 Переглянути ДЗ")
async def show_hw(message: Message):
    if not homework:
        await message.answer(
            "🎉 **Наразі немає невиконаних домашніх завдань!**",
            parse_mode="Markdown",
        )
        return

    text = "📚 **СПИСОК ДОМАШНІХ ЗАВДАНЬ:**\n━━━━━━━━━━━━━━━━━━━\n\n"

    user_id = message.from_user.id

    homework = await get_homework(user_id)

    for hw in  homework:
        text  += (
            f"📚 **Предмет:** {hw[1]}\n"
            f"📝 **Завдання:** {hw[2]}\n"
            f"⏰ **Дедлайн:** {hw[3]}"
        )

        await message.answer(text, parse_mode="Markdown")
