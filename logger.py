import logging
import os
from pathlib import Path
from config import LOG_LEVEL, LOG_FORMAT

# Создаем директорию для логов, если она не существует
log_dir = Path(__file__).parent / 'logs'
os.makedirs(log_dir, exist_ok=True)

# Настраиваем логгер
logger = logging.getLogger('selfrealization_bot')
logger.setLevel(LOG_LEVEL)

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler(log_dir / 'bot.log')
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler) 