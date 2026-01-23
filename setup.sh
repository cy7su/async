#!/bin/bash

echo "Настройка виртуального окружения для async..."

# Проверить и установить python3-venv если нужно
if ! dpkg -l | grep -q python3-venv; then
    echo "Установка python3-venv..."
    apt update && apt install -y python3-venv
fi

# Создать виртуальное окружение если не существует
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активировать и установить зависимости
echo "Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Настройка завершена! Используйте 'source venv/bin/activate && python run.py' для запуска."
