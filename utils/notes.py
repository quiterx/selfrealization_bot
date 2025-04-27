import aiosqlite
from datetime import datetime
from .database import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                content TEXT
            )
        ''')
        await db.commit()

async def add_note(user_id: int, note_type: str, content: str):
    """Добавление заметки"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO notes (user_id, date, type, content)
            VALUES (?, ?, ?, ?)
        ''', (user_id, today, note_type, content))
        await db.commit()

async def get_today_notes(user_id: int):
    """Получение заметок за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT type, content
            FROM notes
            WHERE user_id = ? AND date = ?
            ORDER BY id DESC
        ''', (user_id, today)) as cursor:
            return await cursor.fetchall()

async def get_history(user_id: int, days: int = 7):
    """Получение истории заметок"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, type, content
            FROM notes
            WHERE user_id = ? AND date >= date('now', ? || ' days')
            ORDER BY date DESC, id DESC
        ''', (user_id, f'-{days}')) as cursor:
            return await cursor.fetchall()

async def delete_note(note_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        await db.commit() 