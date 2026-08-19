SCHEDULER_LIST = []
REMINDERS_LIST = []

import aiosqlite


import os
from pathlib import Path

# Отримуємо шлях до директорії, де лежить сам файл database.py
BASE_DIR = Path(__file__).resolve().parent

# Тепер шляхи будуть коректними незалежно від ОС
HM_NAME = os.path.join(BASE_DIR, 'homework_database.db')
GB_NAME = os.path.join(BASE_DIR, 'grades_datebase.db')
RB_NAME = os.path.join(BASE_DIR, 'remimbers_database.db')

async def init_db():
    async with aiosqlite.connect(HM_NAME) as db:
        await db.execute('''
    CREATE TABLE IF NOT EXISTS homework(
    hm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    task TEXT,  
    dedline TEXT,
    user_id INTEGER 
    )
''')
        await db.commit()
        print("База даних №1 готова до роботи")

    async with aiosqlite.connect(GB_NAME) as gb:
        await gb.execute('''
        CREATE TABLE IF NOT EXISTS grades(
        grades_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        grades TEXT
        )
''')
        await gb.commit()
        print("БАЗА ДАНИХ №2 ГОТОВА ДО РОБОТИ")


    async with aiosqlite.connect(RB_NAME) as rb:
        await rb.execute('''
        CREATE TABLE IF NOT EXISTS remimbers(
        remimbers_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        run_time TEXT
        )
''')
        await rb.commit()
        print("БАЗА ДАНИХ №3 ГОТОВА ДО РОБОТИ")



async def get_remimbers(user_id: int):
    async with aiosqlite.connect(RB_NAME) as rb:
        async with rb.execute(
            """
            SELECT remimbers_id, user_id, text, run_time 
            FROM remimbers WHERE user_id = ?
        """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchall()

        if row:
            return{
                "remimbers_id": row[0],
                "user_id": row[1],
                "text": row[2],
                "run_time": row[3]
            }
        return None




async def get_homework(user_id: int):
    async with aiosqlite.connect(HM_NAME) as hw:
        async with hw.execute(
            """
            SELECT hm_id, subject, task, dedline, user_id 
            FROM homework WHERE user_id = ?
        """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchall()

        if row:
            return{
                "hm_id": row[0],
                "subject": row[1],
                "task": row[2],
                "dedline": row[3],
                "user_id": row[4]    
            }
        return None


async def save_grades(user_id: int, subject: str, new_grades: str):
    async with aiosqlite.connect(GB_NAME) as gb:
        # Перевіряємо, чи є вже запис для цього предмета у користувача
        async with gb.execute(
            "SELECT grades FROM grades WHERE user_id = ? AND subject = ?", 
            (user_id, subject)
        ) as cursor:
            row = await cursor.fetchone()
            
        if row:
            # Якщо є — оновлюємо, додаючи нові оцінки через кому[cite: 3]
            old_grades = row[0]
            updated_grades = f"{old_grades}, {new_grades}"
            await gb.execute(
                "UPDATE grades SET grades = ? WHERE user_id = ? AND subject = ?",
                (updated_grades, user_id, subject)
            )
        else:
            # Якщо немає — створюємо новий запис[cite: 3]
            await gb.execute(
                "INSERT INTO grades (user_id, subject, grades) VALUES (?, ?, ?)",
                (user_id, subject, new_grades)
            )
        await gb.commit()


async def get_user_subject_grades(user_id: int, subject: str):
    async with aiosqlite.connect(GB_NAME) as gb:
        async with gb.execute(
            "SELECT grades FROM grades WHERE user_id = ? AND subject = ?",
            (user_id, subject)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None