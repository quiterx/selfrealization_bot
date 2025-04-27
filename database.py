import os
import aiosqlite
from pathlib import Path

# Путь к базе данных
DB_PATH = Path(__file__).parent / 'data' / 'bot.db'

# Создаем директорию для базы данных, если она не существует
os.makedirs(DB_PATH.parent, exist_ok=True)

async def get_db():
    """Получить подключение к базе данных"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    """Инициализировать базу данных"""
    async with get_db() as db:
        # Создаем таблицы
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS calories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                calories INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS water (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                amount INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                steps INTEGER,
                minutes INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS weight (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                weight REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                text TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                time TIME,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS motivation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                category TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS coach_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                category TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                category TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.commit() 