from aiogram import Router, F
from aiogram.types import (
    Message,

)
from keyboard.inline import main_keyboard

back_router = Router()


# --- НАВІГАЦІЯ ---
@back_router.message(F.text == "⬅️ Назад")
async def back(message: Message):
    await message.answer(
        "🔄 Повертаємось у головне меню:", reply_markup=main_keyboard()
    )

