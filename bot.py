import asyncio
import logging
import os
import random
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from utils.database import init_db, create_user
from utils.motivation import init_motivation_db, get_random_motivation, get_random_nutrition_tip, get_random_fitness_tip
from utils.coach import init_coach_db, get_coach_answer
from utils.faq import init_faq_db, get_faq_list, get_faq_answer, add_user_question
from utils import calories, water, activity, weight, notes
from utils.reminders import Reminders

# Настройка логирования
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Загрузка переменных окружения
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения")
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽 Калории"), KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="🏃‍♂️ Активность"), KeyboardButton(text="⚖️ Вес")],
        [KeyboardButton(text="📅 Планы и мысли"), KeyboardButton(text="🤖 Совет дня")],
        [KeyboardButton(text="❓ Вопрос тренеру")],
    ],
    resize_keyboard=True
)

# Кнопки для трекера калорий
calories_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➖ Вычесть калории"), KeyboardButton(text="🔄 Сбросить остаток")],
        [KeyboardButton(text="✏️ Изменить лимит"), KeyboardButton(text="📊 История")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Кнопки для трекера воды
water_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➖ Выпил воды"), KeyboardButton(text="🔄 Сбросить воду")],
        [KeyboardButton(text="✏️ Изменить лимит воды"), KeyboardButton(text="📊 История воды")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Кнопки для трекера активности
activity_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить шаги"), KeyboardButton(text="🏋️‍♂️ Отметить тренировку")],
        [KeyboardButton(text="🔄 Сбросить активность"), KeyboardButton(text="📊 История активности")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Кнопки для трекера веса
weight_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Ввести вес"), KeyboardButton(text="🔄 Сбросить вес")],
        [KeyboardButton(text="📊 История веса")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Кнопки для раздела планов и мыслей
notes_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Записать план"), KeyboardButton(text="💭 Записать мысль")],
        [KeyboardButton(text="📋 Сегодняшние записи"), KeyboardButton(text="📚 История записей")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Кнопки для раздела FAQ
faq_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Частые вопросы"), KeyboardButton(text="✍️ Задать свой вопрос")],
        [KeyboardButton(text="⬅️ В меню")],
    ],
    resize_keyboard=True
)

# Создаем объект для напоминаний
reminders = None

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        global reminders
        if not reminders:
            reminders = Reminders(bot)
        
        # Инициализируем базу данных
        await init_db()
        await init_motivation_db()
        await init_coach_db()
        await init_faq_db()
        
        # Создаем пользователя
        await create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Устанавливаем пользователя для напоминаний
        reminders.set_user(message.from_user.id)
        await reminders.start()
        
        await message.answer(
            "Привет! 👋\n\nЯ твой бот-помощник для самореализации и похудения! Вместе мы сможем достичь твоих целей: следить за калориями, водой, активностью и поддерживать мотивацию каждый день! 💪\n\nЯ буду напоминать тебе пить воду и отправлять мотивирующие сообщения!\n\nВыбери раздел:",
            reply_markup=main_menu
        )
        logger.info(f"Новый пользователь: {message.from_user.id} ({message.from_user.username})")
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message()
async def handle_menu(message: types.Message):
    try:
        text = message.text
        user_id = message.from_user.id
        logger.info(f"Пользователь {user_id} отправил сообщение: {text}")
        
        if text == "🤖 Совет дня":
            tip = await get_random_nutrition_tip() if random.choice([True, False]) else await get_random_fitness_tip()
            await message.answer(f"Совет дня: {tip}")
        elif text == "❓ Вопрос тренеру":
            await message.answer(
                "Ты можешь выбрать частый вопрос или задать свой!",
                reply_markup=faq_menu
            )
        elif text == "📅 Планы и мысли":
            await message.answer(
                "Здесь ты можешь записывать свои планы и мысли. Это поможет отслеживать прогресс и анализировать свой путь!",
                reply_markup=notes_menu
            )
        elif text == "🍽 Калории":
            today = await calories.get_today(user_id)
            await message.answer(
                f"🍽 Трекер калорий\n\nЛимит: {today['limit']} ккал\nОсталось: {today['left']} ккал\n\nЧто сделать?",
                reply_markup=calories_menu
            )
        elif text == "�� Вода":
            today = await water.get_today(user_id)
            await message.answer(
                f"💧 Трекер воды\n\nЛимит: {today['limit']} мл\nОсталось: {today['left']} мл\n\nЧто сделать?",
                reply_markup=water_menu
            )
        elif text == "🏃‍♂️ Активность":
            today = await activity.get_today(user_id)
            workout = "✅" if today['workout'] else "❌"
            await message.answer(
                f"🏃‍♂️ Трекер активности\n\nШаги: {today['steps']}\nТренировка: {workout}\n\nЧто сделать?",
                reply_markup=activity_menu
            )
        elif text == "⚖️ Вес":
            today = await weight.get_today(user_id)
            msg = f"⚖️ Трекер веса\n\nТекущий вес: {today if today else 'не введён'} кг\n\nЧто сделать?"
            await message.answer(msg, reply_markup=weight_menu)
        elif text == "➖ Вычесть калории":
            await message.answer("Сколько калорий вычесть? Введите число:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "subtract_calories"
        elif text == "🔄 Сбросить остаток":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_calories")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_reset")],
            ])
            await message.answer("Вы точно уверены, что хотите обнулить остаток калорий на сегодня?", reply_markup=kb)
        elif text == "✏️ Изменить лимит":
            await message.answer("Введите новый лимит калорий на день:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "set_limit"
        elif text == "📊 История":
            hist = await calories.get_history(user_id, 7)
            msg = "История за 7 дней:\n"
            for d, lim, left in reversed(hist):
                used = lim - left
                msg += f"{d}: {used}/{lim} ккал\n"
            await message.answer(msg)
        elif text == "➖ Выпил воды":
            await message.answer("Сколько мл воды выпито? Введите число:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "subtract_water"
        elif text == "🔄 Сбросить воду":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_water")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_reset_water")],
            ])
            await message.answer("Вы точно уверены, что хотите обнулить остаток воды на сегодня?", reply_markup=kb)
        elif text == "✏️ Изменить лимит воды":
            await message.answer("Введите новый лимит воды на день (в мл):", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "set_water_limit"
        elif text == "📊 История воды":
            hist = await water.get_history(user_id, 7)
            msg = "История воды за 7 дней:\n"
            for d, lim, left in reversed(hist):
                used = lim - left
                msg += f"{d}: {used}/{lim} мл\n"
            await message.answer(msg)
        elif text == "➕ Добавить шаги":
            await message.answer("Сколько шагов добавить? Введите число:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "add_steps"
        elif text == "🏋️‍♂️ Отметить тренировку":
            await activity.add_workout(user_id)
            await message.answer("Тренировка отмечена! 💪", reply_markup=activity_menu)
        elif text == "🔄 Сбросить активность":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_activity")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_reset_activity")],
            ])
            await message.answer("Вы точно уверены, что хотите сбросить активность за сегодня?", reply_markup=kb)
        elif text == "�� История активности":
            hist = await activity.get_history(user_id, 7)
            msg = "История активности за 7 дней:\n"
            for d, steps, workout in reversed(hist):
                w = "✅" if workout else "❌"
                msg += f"{d}: {steps} шагов, тренировка: {w}\n"
            await message.answer(msg)
        elif text == "➕ Ввести вес":
            await message.answer("Введи свой вес (кг):", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "add_weight"
        elif text == "🔄 Сбросить вес":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_weight")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_reset_weight")],
            ])
            await message.answer("Ты точно хочешь удалить вес за сегодня?", reply_markup=kb)
        elif text == "📊 История веса":
            hist = await weight.get_history(user_id, 14)
            msg = "История веса за 2 недели:\n"
            for d, v in reversed(hist):
                msg += f"{d}: {v} кг\n"
            await message.answer(msg)
        elif text == "📝 Записать план":
            await message.answer("Напиши свой план:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "add_plan"
        elif text == "💭 Записать мысль":
            await message.answer("Запиши свою мысль:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "add_thought"
        elif text == "📋 Сегодняшние записи":
            today_notes = await notes.get_today_notes(user_id)
            if today_notes:
                msg = "Записи за сегодня:\n\n"
                for type_, content in today_notes:
                    emoji = "📝" if type_ == "plan" else "💭"
                    msg += f"{emoji} {content}\n"
            else:
                msg = "На сегодня пока нет записей."
            await message.answer(msg, reply_markup=notes_menu)
        elif text == "📚 История записей":
            hist = await notes.get_history(user_id, 7)
            if hist:
                msg = "История записей за неделю:\n\n"
                current_date = None
                for date, type_, content in hist:
                    if date != current_date:
                        current_date = date
                        msg += f"\n📅 {date}:\n"
                    emoji = "📝" if type_ == "plan" else "💭"
                    msg += f"{emoji} {content}\n"
            else:
                msg = "История пуста."
            await message.answer(msg)
        elif text == "❓ Частые вопросы":
            faq_list = await get_faq_list()
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=q, callback_data=f"faq_{id}")] for id, q, _ in faq_list
            ])
            await message.answer("Выбери вопрос:", reply_markup=kb)
        elif text == "✍️ Задать свой вопрос":
            await message.answer("Напиши свой вопрос тренеру:", reply_markup=ReplyKeyboardRemove())
            dp.fsm_state = "ask_question"
        elif text == "⬅️ В меню":
            await message.answer("Выбери раздел:", reply_markup=main_menu)
        elif dp.fsm_state == "subtract_calories":
            try:
                amount = int(text)
                await calories.add_calories(user_id, amount)
                today = await calories.get_today(user_id)
                await message.answer(
                    f"✅ Вычтено {amount} ккал\n\nОсталось: {today['left']} ккал",
                    reply_markup=calories_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "set_limit":
            try:
                limit = int(text)
                await calories.set_limit(user_id, limit)
                await message.answer(
                    f"✅ Лимит калорий установлен: {limit} ккал",
                    reply_markup=calories_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "subtract_water":
            try:
                amount = int(text)
                await water.add_water(user_id, amount)
                today = await water.get_today(user_id)
                await message.answer(
                    f"✅ Добавлено {amount} мл воды\n\nОсталось: {today['left']} мл",
                    reply_markup=water_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "set_water_limit":
            try:
                limit = int(text)
                await water.set_limit(user_id, limit)
                await message.answer(
                    f"✅ Лимит воды установлен: {limit} мл",
                    reply_markup=water_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "add_steps":
            try:
                steps = int(text)
                await activity.add_steps(user_id, steps)
                today = await activity.get_today(user_id)
                await message.answer(
                    f"✅ Добавлено {steps} шагов\n\nВсего: {today['steps']} шагов",
                    reply_markup=activity_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "add_weight":
            try:
                weight_value = float(text)
                await weight.add_weight(user_id, weight_value)
                await message.answer(
                    f"✅ Вес {weight_value} кг сохранен",
                    reply_markup=weight_menu
                )
                dp.fsm_state = None
            except ValueError:
                await message.answer("Пожалуйста, введите число:")
        elif dp.fsm_state == "add_plan":
            await notes.add_note(user_id, "plan", text)
            await message.answer(
                "✅ План сохранен",
                reply_markup=notes_menu
            )
            dp.fsm_state = None
        elif dp.fsm_state == "add_thought":
            await notes.add_note(user_id, "thought", text)
            await message.answer(
                "✅ Мысль сохранена",
                reply_markup=notes_menu
            )
            dp.fsm_state = None
        elif dp.fsm_state == "ask_question":
            await add_user_question(user_id, text)
            answer = await get_coach_answer(text)
            await message.answer(
                f"Спасибо за вопрос! Вот мой ответ:\n\n{answer}",
                reply_markup=faq_menu
            )
            dp.fsm_state = None
    except Exception as e:
        logger.error(f"Ошибка в handle_menu: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    try:
        user_id = call.from_user.id
        logger.info(f"Пользователь {user_id} нажал кнопку: {call.data}")
        
        if call.data == "reset_calories":
            await calories.reset_calories(user_id)
            await call.message.answer("✅ Остаток калорий сброшен", reply_markup=calories_menu)
        elif call.data == "cancel_reset":
            await call.message.answer("Действие отменено", reply_markup=calories_menu)
        elif call.data == "reset_water":
            await water.reset_water(user_id)
            await call.message.answer("✅ Остаток воды сброшен", reply_markup=water_menu)
        elif call.data == "cancel_reset_water":
            await call.message.answer("Действие отменено", reply_markup=water_menu)
        elif call.data == "reset_activity":
            await activity.reset_activity(user_id)
            await call.message.answer("✅ Активность сброшена", reply_markup=activity_menu)
        elif call.data == "cancel_reset_activity":
            await call.message.answer("Действие отменено", reply_markup=activity_menu)
        elif call.data == "reset_weight":
            await weight.reset_weight(user_id)
            await call.message.answer("✅ Вес сброшен", reply_markup=weight_menu)
        elif call.data == "cancel_reset_weight":
            await call.message.answer("Действие отменено", reply_markup=weight_menu)
        elif call.data.startswith("faq_"):
            faq_id = int(call.data[4:])
            question, answer = await get_faq_answer(faq_id)
            await call.message.answer(
                f"❓ {question}\n\n{answer}",
                reply_markup=faq_menu
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_callback: {e}")
        await call.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def main():
    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 