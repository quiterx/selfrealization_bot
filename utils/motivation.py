import aiosqlite
import random
from .database import DB_PATH

async def init_motivation_db():
    """Инициализация базы данных с мотивационными сообщениями"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица мотивационных сообщений
        await db.execute('''
            CREATE TABLE IF NOT EXISTS motivation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT CHECK(type IN ('general', 'nutrition', 'fitness'))
            )
        ''')
        
        # Добавляем базовые мотивационные сообщения, если таблица пуста
        async with db.execute('SELECT COUNT(*) FROM motivation') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                messages = [
                    ("Ты сильнее, чем думаешь! 💪", "general"),
                    ("Каждый шаг приближает тебя к цели! 🏃‍♂️", "general"),
                    ("Сегодня - отличный день для новых достижений! 🌟", "general"),
                    ("Помни: ты делаешь это для себя! ❤️", "general"),
                    ("Не сдавайся! Ты уже прошел(а) долгий путь! 🏆", "general"),
                    ("Пейте воду перед едой - это поможет контролировать аппетит! 💧", "nutrition"),
                    ("Выбирайте цельные продукты вместо обработанных! 🥗", "nutrition"),
                    ("Не пропускайте завтрак - это важнейший прием пищи! 🍳", "nutrition"),
                    ("Планируйте приемы пищи заранее! 📝", "nutrition"),
                    ("Слушайте свое тело - оно знает, что ему нужно! 🧘‍♂️", "nutrition"),
                    ("Регулярные тренировки - ключ к успеху! 🏋️‍♂️", "fitness"),
                    ("Не забывайте про разминку перед тренировкой! 🔥", "fitness"),
                    ("Силовые тренировки помогают сжигать калории даже после занятий! 💪", "fitness"),
                    ("Кардио тренировки укрепляют сердце и сжигают жир! 🏃‍♂️", "fitness"),
                    ("Растяжка после тренировки - залог гибкости и отсутствия травм! 🧘‍♀️", "fitness")
                ]
                await db.executemany(
                    'INSERT INTO motivation (content, type) VALUES (?, ?)',
                    messages
                )
                await db.commit()

async def get_random_motivation():
    """Получение случайного мотивационного сообщения"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT content FROM motivation 
            WHERE type = 'general' 
            ORDER BY RANDOM() LIMIT 1
        ''') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "Ты молодец! Продолжай в том же духе! 💪"

async def get_random_nutrition_tip():
    """Получение случайного совета по питанию"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT content FROM motivation 
            WHERE type = 'nutrition' 
            ORDER BY RANDOM() LIMIT 1
        ''') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "Пейте больше воды и ешьте больше овощей! 🥗"

async def get_random_fitness_tip():
    """Получение случайного совета по тренировкам"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT content FROM motivation 
            WHERE type = 'fitness' 
            ORDER BY RANDOM() LIMIT 1
        ''') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "Регулярные тренировки - залог успеха! 💪" 