#!/bin/bash

# Скрипт запуска Telegram бота для сканирования чеков

set -e

echo "🤖 Запуск Telegram бота для сканирования чеков..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте файл .env на основе .env.example и заполните BOT_TOKEN"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Загружаем переменные окружения
source .env

# Проверяем наличие BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не установлен в файле .env!"
    echo "📝 Добавьте BOT_TOKEN в файл .env"
    exit 1
fi

# Создаем необходимые директории
mkdir -p data logs temp

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Проверяем наличие базы данных
if [ ! -f "data/receipts.db" ]; then
    echo "🗄️ Инициализация базы данных..."
    python -c "from database import ReceiptDatabase; ReceiptDatabase('data/receipts.db')"
fi

# Запускаем бота
echo "🚀 Запуск бота..."
python main.py