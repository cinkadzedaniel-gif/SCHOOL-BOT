from datetime import datetime
import aiosqlite
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from database import DB_NAME

canteen_router = Router()

# Тепер замість True/False тримаємо статус: "absent" (❌), "present" (✅), "n" (🔴 Н)
class_attendance = {
    "Андрусяк Т.": "absent",
    "Андрущенко В.": "absent",
    "Білоусько А.": "absent",
    "Валаміна А.": "absent",
    "Вишневський Т.": "absent",
    "Гуріна А.": "absent",
    "Дрозденко Д.": "absent",
    "Климук У.": "absent",
    "Коваленко О.": "absent",
    "Коваль М.": "absent",
    "Кожемякін А.": "absent",
    "Колісніченко О.": "absent",
    "Кондрашова К.": "absent",
    "Костакі В.": "absent",
    "Ляска С.": "absent",
    "Макієвський С.": "absent",
    "Маноха А.": "absent",
    "Мацан Н.": "absent",
    "Мельниченко С.": "absent",
    "Перемот В.": "absent",
    "Петренко П.": "absent",
    "Піддубна С.": "absent",
    "Саусенко М.": "absent",
    "Свіріда О.": "absent",
    "Третяк А.": "absent",
    "Чінкадзе Д.": "absent",
    "Яковлєв А.": "absent",
}

def get_attendance_keyboard(attendance_dict):
    keyboard = []
    for name, status in attendance_dict.items():
        if status == "present":
            icon = "✅"
        elif status == "n":
            icon = "🔴 н"
        else:
            icon = "❌"
            
        keyboard.append([
            InlineKeyboardButton(text=f"{name}: {icon}", callback_data=f"toggle_{name}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="📋 Сформувати та зберегти звіт", callback_data="finish_canteen")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@canteen_router.message(F.text == "Відмітитись для їдальні")
async def cmd_canteen(message: Message):
    await message.answer(
        "Відміть тих, хто присутній (натискай на кнопку, щоб змінити статус: ❌ ➡️ ✅ ➡️ 🔴 н):",
        reply_markup=get_attendance_keyboard(class_attendance)
    )

@canteen_router.callback_query(F.data.startswith("toggle_"))
async def toggle_student(callback: CallbackQuery):
    name = callback.data.split("_", 1)[1]
    if name in class_attendance:
        current_status = class_attendance[name]
        # Зміна станів по колу: absent (❌) -> present (✅) -> n (🔴 н) -> absent (❌)
        if current_status == "absent":
            class_attendance[name] = "present"
        elif current_status == "present":
            class_attendance[name] = "n"
        else:
            class_attendance[name] = "absent"
            
        await callback.message.edit_reply_markup(
            reply_markup=get_attendance_keyboard(class_attendance)
        )
    await callback.answer()

@canteen_router.callback_query(F.data == "finish_canteen")
async def finish_canteen(callback: CallbackQuery):
    # Рахуємо тільки тих, у кого статус "present" (✅)
    present_count = sum(1 for status in class_attendance.values() if status == "present")
    n_count = sum(1 for status in class_attendance.values() if status == "n")
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO attendance_reports (date, count) VALUES (?, ?)",
            (today_str, present_count)
        )
        await db.commit()

    report = f"🍽 8-А — {present_count} учнів прийдуть\n🔴 Точно не буде (н): {n_count}"
    await callback.message.answer(report)

    # Повертаємо всіх у стан "absent" (❌) після збереження звіту
    for name in class_attendance:
        class_attendance[name] = "absent"

    await callback.answer("Звіт сформовано та збережено!")

@canteen_router.message(F.text == "/today_report")
async def cmd_today_report(message: Message):
    today_str = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT count FROM attendance_reports WHERE date = ?", (today_str,)) as cursor:
            row = await cursor.fetchone()

    if row:
        await message.answer(f"📋 Збережений звіт за сьогодні ({today_str}):\n🍽 8-А — {row[0]} учнів")
    else:
        await message.answer("⚠️ За сьогодні звіт ще не був збережений.")