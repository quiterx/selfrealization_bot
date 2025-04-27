import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from .database import DB_PATH
import aiosqlite
from utils.motivation import get_random_motivation, get_random_nutrition_tip, get_random_fitness_tip

class Reminders:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_id = None
        self.water_task = None
        self.motivation_task = None
        self.water_hours = list(range(8, 21, 4))  # 8:00, 12:00, 16:00, 20:00

    def set_user(self, user_id: int):
        """Установка пользователя для напоминаний"""
        self.user_id = user_id

    async def start(self):
        """Запуск напоминаний"""
        if self.water_task:
            self.water_task.cancel()
        if self.motivation_task:
            self.motivation_task.cancel()

        # Запускаем напоминания о воде каждые 2 часа
        self.water_task = asyncio.create_task(self.water_reminder())
        
        # Запускаем мотивационные сообщения каждые 4 часа
        self.motivation_task = asyncio.create_task(self.motivation_reminder())

    async def stop(self):
        """Остановка напоминаний"""
        if self.water_task:
            self.water_task.cancel()
        if self.motivation_task:
            self.motivation_task.cancel()

    async def water_reminder(self):
        """Напоминание о воде"""
        while True:
            try:
                # Проверяем, сколько воды выпито за последние 2 часа
                async with aiosqlite.connect(DB_PATH) as db:
                    two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                    async with db.execute('''
                        SELECT SUM(amount) FROM water 
                        WHERE user_id = ? AND datetime(date || ' ' || time) > ?
                    ''', (self.user_id, two_hours_ago)) as cursor:
                        amount = await cursor.fetchone()
                        amount = amount[0] if amount[0] else 0

                if amount < 200:  # Если выпито меньше 200 мл за 2 часа
                    await self.bot.send_message(
                        self.user_id,
                        "💧 Не забывай пить воду! За последние 2 часа ты выпил(а) мало воды."
                    )
            except Exception as e:
                logging.error(f"Error in water reminder: {e}")

            await asyncio.sleep(7200)  # 2 часа

    async def motivation_reminder(self):
        """Мотивационные сообщения"""
        while True:
            try:
                # Получаем случайную мотивацию из базы данных
                async with aiosqlite.connect(DB_PATH) as db:
                    async with db.execute('''
                        SELECT content FROM motivation 
                        ORDER BY RANDOM() LIMIT 1
                    ''') as cursor:
                        motivation = await cursor.fetchone()
                        if motivation:
                            await self.bot.send_message(
                                self.user_id,
                                f"💪 {motivation[0]}"
                            )
            except Exception as e:
                logging.error(f"Error in motivation reminder: {e}")

            await asyncio.sleep(14400)  # 4 часа

    async def send_water_reminder(self):
        if self.user_id:
            await self.bot.send_message(
                self.user_id,
                "💧 Не забудь попить воды! Это важно для метаболизма и самочувствия."
            )

    async def send_morning_motivation(self):
        if self.user_id:
            tip = get_random_nutrition_tip() if datetime.datetime.now().hour % 2 == 0 else get_random_fitness_tip()
            msg = f"🌅 Доброе утро!\n\n{get_random_motivation()}\n\nСовет дня: {tip}"
            await self.bot.send_message(self.user_id, msg) 