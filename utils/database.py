import aiosqlite
import os
from datetime import datetime

DB_PATH = "data/bot.db"

async def init_db():
    """Инициализация базы данных"""
    os.makedirs("data", exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                daily_calories_limit INTEGER DEFAULT 2000,
                daily_water_limit INTEGER DEFAULT 2000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица калорий
        await db.execute('''
            CREATE TABLE IF NOT EXISTS calories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                calories INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица воды
        await db.execute('''
            CREATE TABLE IF NOT EXISTS water (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                amount INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица активности
        await db.execute('''
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                steps INTEGER DEFAULT 0,
                workout BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица веса
        await db.execute('''
            CREATE TABLE IF NOT EXISTS weight (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                weight REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица заметок
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                type TEXT CHECK(type IN ('plan', 'thought')),
                content TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица целей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                target_date DATE,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица статистики
        await db.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                calories_consumed INTEGER DEFAULT 0,
                water_consumed INTEGER DEFAULT 0,
                steps_taken INTEGER DEFAULT 0,
                workouts_completed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        await db.commit()

async def get_user(user_id: int):
    """Получение информации о пользователе"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'daily_calories_limit': row[4],
                    'daily_water_limit': row[5],
                    'created_at': row[6]
                }
            return None

async def create_user(user_id: int, username: str, first_name: str, last_name: str):
    """Создание нового пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
            (user_id, username, first_name, last_name)
        )
        await db.commit()

async def update_user_limits(user_id: int, calories_limit: int = None, water_limit: int = None):
    """Обновление лимитов пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        if calories_limit is not None:
            await db.execute(
                'UPDATE users SET daily_calories_limit = ? WHERE user_id = ?',
                (calories_limit, user_id)
            )
        if water_limit is not None:
            await db.execute(
                'UPDATE users SET daily_water_limit = ? WHERE user_id = ?',
                (water_limit, user_id)
            )
        await db.commit()

async def get_user_statistics(user_id: int, days: int = 7):
    """Получение статистики пользователя за последние N дней"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, calories_consumed, water_consumed, steps_taken, workouts_completed
            FROM statistics
            WHERE user_id = ? AND date >= date('now', ? || ' days')
            ORDER BY date DESC
        ''', (user_id, f'-{days}')) as cursor:
            return await cursor.fetchall()

async def update_statistics(user_id: int, date: str, **kwargs):
    """Обновление статистики пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существование записи
        async with db.execute(
            'SELECT id FROM statistics WHERE user_id = ? AND date = ?',
            (user_id, date)
        ) as cursor:
            exists = await cursor.fetchone()
            
            if exists:
                # Обновляем существующую запись
                set_clause = ', '.join(f'{k} = ?' for k in kwargs.keys())
                values = list(kwargs.values()) + [user_id, date]
                await db.execute(
                    f'UPDATE statistics SET {set_clause} WHERE user_id = ? AND date = ?',
                    values
                )
            else:
                # Создаем новую запись
                columns = ['user_id', 'date'] + list(kwargs.keys())
                placeholders = ', '.join(['?'] * len(columns))
                values = [user_id, date] + list(kwargs.values())
                await db.execute(
                    f'INSERT INTO statistics ({", ".join(columns)}) VALUES ({placeholders})',
                    values
                )
        await db.commit() 