from datetime import datetime
import aiosqlite
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

canteen_router = Router()

DB_NAME = "attendance.db"

class_attendance = {
    "Андрусяк Т.": False,
    "Андрущенко В.": False,
    "Білоусько А.": False,
    "Валаміна А.": False,
    "Вишневський Т.": False,
    "Гуріна А.": False,
    "Дрозденко Д.": False,
    "Климук У.": False,
    "Коваленко О.": False,
    "Коваль М.": False,
    "Кожемякін А.": False,
    "Колісніченко О.": False,
    "Кондрашова К.": False,
    "Костакі В.": False,
    "Ляска С.": False,
    "Макієвський С.": False,
    "Маноха А.": False,
    "Мацан Н.": False,
    "Мельниченко С.": False,
    "Перемот В.": False,
    "Петренко П.": False,
    "Піддубна С.": False,
    "Саусенко М.": False,
    "Свіріда О.": False,
    "Третяк А.": False,
    "Чінкадзе Д.": False,
    "Яковлєв А.": False,
}


def get_attendance_keyboard(attendance_dict):
    keyboard = []
    for name, status in attendance_dict.items():
        icon = "✅" if status else "❌"
        keyboard.append([
            InlineKeyboardButton(text=f"{name}: {icon}", callback_data=f"toggle_{name}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="📋 Сформувати та зберегти звіт", callback_data="finish_canteen")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text == "Відмітитись для їдальні")
async def cmd_canteen(message: Message):
    await message.answer(
        "Відміть тих, хто присутній:",
        reply_markup=get_attendance_keyboard(class_attendance)
    )

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_student(callback: CallbackQuery):
    name = callback.data.split("_", 1)[1]
    if name in class_attendance:
        class_attendance[name] = not class_attendance[name]
        await callback.message.edit_reply_markup(
            reply_markup=get_attendance_keyboard(class_attendance)
        )
    await callback.answer()

@router.callback_query(F.data == "finish_canteen")
async def finish_canteen(callback: CallbackQuery):
    present_count = sum(1 for status in class_attendance.values() if status)
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO attendance_reports (date, count) VALUES (?, ?)",
            (today_str, present_count)
        )
        await db.commit()

    report = f"🍽 8-А — {present_count} учнів"
    await callback.message.answer(report)

    for name in class_attendance:
        class_attendance[name] = False

    await callback.answer("Звіт сформовано та збережено!")

@router.message(F.text == "/today_report")
async def cmd_today_report(message: Message):
    today_str = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT count FROM attendance_reports WHERE date = ?", (today_str,)) as cursor:
            row = await cursor.fetchone()

    if row:
        await message.answer(f"📋 Збережений звіт за сьогодні ({today_str}):\n🍽 8-А — {row[0]} учнів")
    else:
        await message.answer("⚠️ За сьогодні звіт ще не був збережений.")