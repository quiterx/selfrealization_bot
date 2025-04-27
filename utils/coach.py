import random
import aiosqlite
from .database import DB_PATH

COACH_ANSWERS = [
    "Старайся есть чаще, но маленькими порциями — это помогает ускорить метаболизм!",
    "Не забывай про белок в каждом приёме пищи — он помогает сохранять мышцы при похудении.",
    "Пей больше воды — это важно для обмена веществ и контроля аппетита!",
    "Если хочется сладкого — попробуй заменить фруктами или ягодами.",
    "Не забывай про физическую активность: даже быстрая прогулка — уже вклад в здоровье!",
    "Сон очень важен для похудения — старайся спать не менее 7-8 часов.",
    "Не ругай себя за срывы — главное, что ты продолжаешь идти к цели!",
]

async def init_coach_db():
    """Инициализация базы данных с ответами тренера"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица ответов тренера
        await db.execute('''
            CREATE TABLE IF NOT EXISTS coach_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT CHECK(category IN ('nutrition', 'fitness', 'motivation', 'general'))
            )
        ''')
        
        # Добавляем базовые ответы, если таблица пуста
        async with db.execute('SELECT COUNT(*) FROM coach_answers') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                answers = [
                    ("Как правильно питаться?", "Основные принципы правильного питания:\n1. Ешьте 5-6 раз в день небольшими порциями\n2. Пейте достаточное количество воды\n3. Увеличьте потребление овощей и фруктов\n4. Ограничьте сахар и фастфуд\n5. Следите за балансом белков, жиров и углеводов", "nutrition"),
                    ("Сколько нужно тренироваться?", "Рекомендуется:\n- 150 минут умеренной активности в неделю\n- 2-3 силовые тренировки\n- Не забывать про разминку и заминку\n- Давать мышцам время на восстановление", "fitness"),
                    ("Как не сдаваться?", "Советы по мотивации:\n1. Ставьте реалистичные цели\n2. Отслеживайте прогресс\n3. Находите поддержку\n4. Вознаграждайте себя за достижения\n5. Помните о своей цели", "motivation"),
                    ("С чего начать?", "План действий:\n1. Определите свою цель\n2. Составьте план питания\n3. Начните с простых тренировок\n4. Ведите дневник прогресса\n5. Не торопитесь, главное - регулярность", "general")
                ]
                await db.executemany(
                    'INSERT INTO coach_answers (question, answer, category) VALUES (?, ?, ?)',
                    answers
                )
                await db.commit()

async def get_coach_answer(question: str):
    """Получение ответа тренера на вопрос"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Сначала ищем точное совпадение
        async with db.execute('''
            SELECT answer FROM coach_answers 
            WHERE question = ?
        ''', (question,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            
        # Если точного совпадения нет, ищем похожие вопросы
        async with db.execute('''
            SELECT answer FROM coach_answers 
            WHERE question LIKE ? 
            ORDER BY RANDOM() LIMIT 1
        ''', (f'%{question}%',)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            
        # Если ничего не найдено, возвращаем общий ответ
        return "Спасибо за вопрос! Я рекомендую:\n1. Следовать принципам правильного питания\n2. Регулярно тренироваться\n3. Отслеживать свой прогресс\n4. Не забывать про мотивацию\n5. Консультироваться с профессионалами"

def get_coach_answer():
    return random.choice(COACH_ANSWERS) 