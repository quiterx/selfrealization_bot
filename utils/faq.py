import aiosqlite
from .database import DB_PATH

async def init_faq_db():
    """Инициализация базы данных с часто задаваемыми вопросами"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица FAQ
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT CHECK(category IN ('nutrition', 'fitness', 'motivation', 'general'))
            )
        ''')
        
        # Добавляем базовые вопросы, если таблица пуста
        async with db.execute('SELECT COUNT(*) FROM faq') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                questions = [
                    ("Сколько воды нужно пить в день?", "Рекомендуется выпивать 30-35 мл воды на 1 кг веса тела. Например, при весе 70 кг нужно выпивать около 2-2.5 литров воды в день.", "nutrition"),
                    ("Как часто нужно тренироваться?", "Оптимально тренироваться 3-4 раза в неделю, давая мышцам время на восстановление между тренировками.", "fitness"),
                    ("Как мотивировать себя?", "1. Ставьте конкретные цели\n2. Отслеживайте прогресс\n3. Находите поддержку\n4. Вознаграждайте себя\n5. Визуализируйте результат", "motivation"),
                    ("С чего начать похудение?", "1. Рассчитайте свой дневной калораж\n2. Начните с простых тренировок\n3. Ведите дневник питания\n4. Пейте достаточно воды\n5. Высыпайтесь", "general")
                ]
                await db.executemany(
                    'INSERT INTO faq (question, answer, category) VALUES (?, ?, ?)',
                    questions
                )
                await db.commit()

async def get_faq_list():
    """Получение списка часто задаваемых вопросов"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT id, question, category 
            FROM faq 
            ORDER BY category, id
        ''') as cursor:
            return await cursor.fetchall()

async def get_faq_answer(faq_id: int):
    """Получение ответа на вопрос FAQ"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT question, answer 
            FROM faq 
            WHERE id = ?
        ''', (faq_id,)) as cursor:
            return await cursor.fetchone()

async def add_user_question(user_id: int, question: str):
    """Добавление вопроса пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO user_questions (user_id, question, date)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, question))
        await db.commit() 