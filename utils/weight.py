import aiosqlite
from datetime import datetime
from .database import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS weight (
                date TEXT PRIMARY KEY,
                value REAL
            )
        ''')
        await db.commit()

async def add_weight(user_id: int, weight: float):
    """Добавление веса"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существование записи
        async with db.execute('''
            SELECT id FROM weight 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            exists = await cursor.fetchone()
            
            if exists:
                # Обновляем существующую запись
                await db.execute('''
                    UPDATE weight 
                    SET weight = ? 
                    WHERE user_id = ? AND date = ?
                ''', (weight, user_id, today))
            else:
                # Создаем новую запись
                await db.execute('''
                    INSERT INTO weight (user_id, date, weight)
                    VALUES (?, ?, ?)
                ''', (user_id, today, weight))
        
        await db.commit()

async def get_today(user_id: int):
    """Получение веса за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT weight 
            FROM weight 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_history(user_id: int, days: int = 14):
    """Получение истории веса"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, weight
            FROM weight
            WHERE user_id = ? AND date >= date('now', ? || ' days')
            ORDER BY date DESC
        ''', (user_id, f'-{days}')) as cursor:
            return await cursor.fetchall()

async def reset_weight(user_id: int):
    """Сброс веса за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            DELETE FROM weight 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        await db.commit() 