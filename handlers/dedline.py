from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard.inline import dedline_keyboard, main_keyboard 
from database import add_dedline


dedline_router = Router()

class Dedline(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_description = State()


@dedline_router.message(F.text == "Дедлайни")
async def  menu (message:Message):
    await message.answer("Оберіть дію", reply_markup=dedline_keyboard())

@dedline_router.message(F.text == "Додати дедлайн")
async def add_dedlina(message:Message, state: FSMContext):
    await message.answer("Напишіть назву дедлайну")
    await state.set_state(Dedline.waiting_for_name)

@dedline_router.message(Dedline.waiting_for_name)
async def waiting_name(message:Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Чудово, тепер напишіть дату на яку встановлюємо цей дедлайн")
    await state.set_state(Dedline.waiting_for_date)

@dedline_router.message(Dedline.waiting_for_date)
async def waiting_data(message:Message, state: FSMContext):
    await state.update_data(date = message.text)
    await message.answer("Введіть опис дедлайна")
    await state.set_state(Dedline.waiting_for_description)

@dedline_router.message(Dedline.waiting_for_description)
async def waiting_discription(message:Message, state: FSMContext):
    discription = message.text

    user_date = await state.get_data()
    title = user_date.get("name")
    date = user_date.get("date")
    user_id = message.from_user.id

    await add_dedline(title, date, discription, user_id )

    state.clear()

    text = (
        "ДЕДЛАЙН ВСТАНОВЛЕННО!!!!\n"
        f"Назва: {title}\n"
        f"Дата дедлайна {date}\n"
        f"Опис: {discription}"
    )
    await message.answer(text, parse_mode = "Markdown", reply_markup = main_keyboard())

    await state.clear()