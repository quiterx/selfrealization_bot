import aiosqlite
from datetime import datetime
from .database import DB_PATH, update_statistics

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS calories (
                date TEXT PRIMARY KEY,
                limit INTEGER,
                left INTEGER
            )
        ''')
        await db.commit()

async def get_today(user_id: int):
    """Получение информации о калориях за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем лимит пользователя
        async with db.execute('SELECT daily_calories_limit FROM users WHERE user_id = ?', (user_id,)) as cursor:
            limit = await cursor.fetchone()
            if not limit:
                return {'limit': 2000, 'left': 2000}
            limit = limit[0]
            
        # Получаем потребленные калории
        async with db.execute('''
            SELECT SUM(calories) FROM calories 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            consumed = await cursor.fetchone()
            consumed = consumed[0] if consumed[0] else 0
            
        return {
            'limit': limit,
            'left': max(0, limit - consumed)
        }

async def add_calories(user_id: int, amount: int):
    """Добавление калорий"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO calories (user_id, date, calories)
            VALUES (?, ?, ?)
        ''', (user_id, today, amount))
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            calories_consumed=amount
        )

async def reset_calories(user_id: int):
    """Сброс калорий за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            DELETE FROM calories 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            calories_consumed=0
        )

async def get_history(user_id: int, days: int = 7):
    """Получение истории калорий"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, daily_calories_limit, 
                   COALESCE(SUM(calories), 0) as consumed
            FROM users
            LEFT JOIN calories ON users.user_id = calories.user_id 
                AND calories.date >= date('now', ? || ' days')
            WHERE users.user_id = ?
            GROUP BY date, daily_calories_limit
            ORDER BY date DESC
        ''', (f'-{days}', user_id)) as cursor:
            return await cursor.fetchall()

async def set_limit(user_id: int, limit: int):
    """Установка лимита калорий"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users 
            SET daily_calories_limit = ? 
            WHERE user_id = ?
        ''', (limit, user_id))
        await db.commit()

async def subtract(amount):
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT left FROM calories WHERE date = ?', (today,))
        row = await cur.fetchone()
        if row:
            left = max(0, row[0] - amount)
            await db.execute('UPDATE calories SET left = ? WHERE date = ?', (left, today))
            await db.commit()
            return left
        return None

async def reset_today():
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT limit FROM calories WHERE date = ?', (today,))
        row = await cur.fetchone()
        if row:
            await db.execute('UPDATE calories SET left = ? WHERE date = ?', (row[0], today))
            await db.commit() 