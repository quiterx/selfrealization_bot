import aiosqlite
from datetime import datetime
from .database import DB_PATH, update_statistics

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS activity (
                date TEXT PRIMARY KEY,
                steps INTEGER,
                workout INTEGER
            )
        ''')
        await db.commit()

async def get_today(user_id: int):
    """Получение информации об активности за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT steps, workout 
            FROM activity 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    'steps': row[0],
                    'workout': bool(row[1])
                }
            else:
                return {
                    'steps': 0,
                    'workout': False
                }

async def add_steps(user_id: int, steps: int):
    """Добавление шагов"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существование записи
        async with db.execute('''
            SELECT steps FROM activity 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            row = await cursor.fetchone()
            
            if row:
                # Обновляем существующую запись
                new_steps = row[0] + steps
                await db.execute('''
                    UPDATE activity 
                    SET steps = ? 
                    WHERE user_id = ? AND date = ?
                ''', (new_steps, user_id, today))
            else:
                # Создаем новую запись
                await db.execute('''
                    INSERT INTO activity (user_id, date, steps)
                    VALUES (?, ?, ?)
                ''', (user_id, today, steps))
        
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            steps_taken=steps
        )

async def add_workout(user_id: int):
    """Добавление тренировки"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существование записи
        async with db.execute('''
            SELECT workout FROM activity 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today)) as cursor:
            row = await cursor.fetchone()
            
            if row:
                # Обновляем существующую запись
                await db.execute('''
                    UPDATE activity 
                    SET workout = TRUE 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))
            else:
                # Создаем новую запись
                await db.execute('''
                    INSERT INTO activity (user_id, date, workout)
                    VALUES (?, ?, TRUE)
                ''', (user_id, today))
        
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            workouts_completed=1
        )

async def reset_activity(user_id: int):
    """Сброс активности за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            DELETE FROM activity 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        await db.commit()
        
        # Обновляем статистику
        await update_statistics(
            user_id=user_id,
            date=today,
            steps_taken=0,
            workouts_completed=0
        )

async def get_history(user_id: int, days: int = 7):
    """Получение истории активности"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT date, steps, workout
            FROM activity
            WHERE user_id = ? AND date >= date('now', ? || ' days')
            ORDER BY date DESC
        ''', (user_id, f'-{days}')) as cursor:
            return await cursor.fetchall() 