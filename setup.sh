#!/bin/bash

# Обновляем систему
sudo apt update
sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv git

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем директорию для логов
mkdir -p logs

# Настраиваем права доступа
chmod +x bot.py
chmod +x setup.sh

# Копируем сервисный файл
sudo cp bot.service /etc/systemd/system/

# Перезагружаем systemd
sudo systemctl daemon-reload

# Запускаем сервис
sudo systemctl enable bot.service
sudo systemctl start bot.service

# Проверяем статус
sudo systemctl status bot.service 