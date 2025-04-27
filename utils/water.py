import aiosqlite
from datetime import datetime
from .database import DB_PATH, update_statistics

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS water (
                date TEXT PRIMARY KEY,
                limit INTEGER,
                left INTEGER
            )
        ''')
        await db.commit()

async def get_today(user_id: int):
    """Получение информации о воде за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем лимит пользователя
        async with db.execute('SELECT daily_water_limit FROM users WHERE user_id = ?', (user_id,)) as cursor:
            limit = await cursor.fetchone()
            if not limit:
                return {'limit': 2000, 'left': 2000}
            limit = limit[0]
            
        # Получаем выпитую воду
        async with db.execute('''
            SELECT SUM(amount) FROM water 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            consumed = await cursor.fetchone()
            consumed = consumed[0] if consumed[0] else 0
            
        return {
            'limit': limit,
            'left': max(0, limit - consumed)
        }

async def add_water(user_id: int, amount: int):
    """Добавление выпитой воды"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO water (user_id, date, amount)
            VALUES (?, ?, ?)
        ''', (user_id, today, amount))
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            water_consumed=amount
        )

async def reset_water(user_id: int):
    """Сброс воды за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            DELETE FROM water 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            water_consumed=0
        )

async def get_history(user_id: int, days: int = 7):
    """Получение истории воды"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, daily_water_limit, 
                   COALESCE(SUM(amount), 0) as consumed
            FROM users
            LEFT JOIN water ON users.user_id = water.user_id 
                AND water.date >= date('now', ? || ' days')
            WHERE users.user_id = ?
            GROUP BY date, daily_water_limit
            ORDER BY date DESC
        ''', (f'-{days}', user_id)) as cursor:
            return await cursor.fetchall()

async def set_limit(user_id: int, limit: int):
    """Установка лимита воды"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users 
            SET daily_water_limit = ? 
            WHERE user_id = ?
        ''', (limit, user_id))
        await db.commit()

async def subtract(amount):
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT left FROM water WHERE date = ?', (today,))
        row = await cur.fetchone()
        if row:
            left = max(0, row[0] - amount)
            await db.execute('UPDATE water SET left = ? WHERE date = ?', (left, today))
            await db.commit()
            return left
        return None

async def reset_today():
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT limit FROM water WHERE date = ?', (today,))
        row = await cur.fetchone()
        if row:
            await db.execute('UPDATE water SET left = ? WHERE date = ?', (row[0], today))
            await db.commit() 