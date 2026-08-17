from aiogram.filters import Command, CommandStart
from aiogram import Router
from aiogram.types import Message
from keyboard.inline import main_keyboard


start_router = Router()



# --- СТАРТ ---
@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привіт, **{message.from_user.first_name}**!\n\n"
        f"Я твій шкільний помічник 🤖. Обирай дію в меню нижче:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )