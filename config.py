import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настройки базы данных
DB_PATH = 'data/bot.db'

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Настройки для напоминаний
REMINDER_CHECK_INTERVAL = 60  # секунды

# Категории для мотивационных сообщений
MOTIVATION_CATEGORIES = ['fitness', 'nutrition', 'general']

# Категории для FAQ и ответов тренера
FAQ_CATEGORIES = ['nutrition', 'fitness', 'motivation', 'general']

# Настройки для отслеживания активности
DEFAULT_STEPS_GOAL = 10000
DEFAULT_MINUTES_GOAL = 30

# Настройки для отслеживания воды
DEFAULT_WATER_GOAL = 2000  # мл

# Настройки для отслеживания калорий
DEFAULT_CALORIES_GOAL = 2000 