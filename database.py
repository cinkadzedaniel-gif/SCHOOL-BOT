SCHEDULER_LIST = []
REMINDERS_LIST = []

import aiosqlite
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_NAME = os.path.join(BASE_DIR, 'centeen_database.db')
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
        # Також створюємо тут таблицю для дедлайнів, щоб усе лежало в безпеці
        await rb.execute('''
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                deadline_date TEXT,
                description TEXT,
                calendar_event_id TEXT
            )
        ''')
        await rb.commit()
        print("БАЗА ДАНИХ №3 ГОТОВА ДО РОБОТИ")


        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS attendance_reports (
                date TEXT PRIMARY KEY,
                count INTEGER
            )
        """)
            await db.commit()

async def get_remimbers(user_id: int):
    async with aiosqlite.connect(RB_NAME) as rb:
        async with rb.execute(
            """
            SELECT remimbers_id, user_id, text, run_time 
            FROM remimbers WHERE user_id = ?
        """,
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()

        if rows:
            return [{
                "remimbers_id": row[0],
                "user_id": row[1],
                "text": row[2],
                "run_time": row[3]
            } for row in rows]
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
            rows = await cursor.fetchall()

        if rows:
            return [{
                "hm_id": row[0],
                "subject": row[1],
                "task": row[2],
                "dedline": row[3],
                "user_id": row[4]
            } for row in rows]
        return None

async def save_grades(user_id: int, subject: str, new_grades: str):
    async with aiosqlite.connect(GB_NAME) as gb:
        async with gb.execute(
            "SELECT grades FROM grades WHERE user_id = ? AND subject = ?", 
            (user_id, subject)
        ) as cursor:
            row = await cursor.fetchone()
            
        if row:
            old_grades = row[0]
            updated_grades = f"{old_grades}, {new_grades}"
            await gb.execute(
                "UPDATE grades SET grades = ? WHERE user_id = ? AND subject = ?",
                (updated_grades, user_id, subject)
            )
        else:
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

async def add_dedline(title: str, date: str, discription: str, user_id: int, calendar_event_id: str):
    async with aiosqlite.connect(RB_NAME) as rb:  
        await rb.execute('''
            INSERT INTO deadlines (title, deadline_date, description, user_id, calendar_event_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, date, discription, user_id, calendar_event_id))
        await rb.commit()

async def get_dedlines(user_id: int):
    async with aiosqlite.connect(RB_NAME) as rb:
        rb.row_factory = aiosqlite.Row
        async with rb.execute('SELECT id, title, deadline_date, description FROM deadlines WHERE user_id = ?', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def delete_deadline_from_db(deadline_id: int):
    async with aiosqlite.connect(RB_NAME) as rb:
        async with rb.execute('SELECT calendar_event_id FROM deadlines WHERE id = ?', (deadline_id,)) as cursor:
            row = await cursor.fetchone()
            calendar_event_id = row[0] if row else None

        await rb.execute('DELETE FROM deadlines WHERE id = ?', (deadline_id,))
        await rb.commit()
        return calendar_event_id