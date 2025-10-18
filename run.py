#!/usr/bin/env python3
"""
Скрипт для запуска бота с проверкой конфигурации
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def check_environment():
    """Проверка переменных окружения"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'GOOGLE_CREDENTIALS_JSON',
        'GOOGLE_SPREADSHEET_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nСоздайте файл .env на основе .env.example")
        return False
    
    print("✅ Все переменные окружения настроены")
    return True

def main():
    """Основная функция"""
    print("🤖 Запуск Telegram бота для сканирования чеков")
    print("=" * 50)
    
    # Проверяем конфигурацию
    if not check_environment():
        sys.exit(1)
    
    # Импортируем и запускаем бота
    try:
        from main import main as bot_main
        print("🚀 Запуск бота...")
        bot_main()
    except KeyboardInterrupt:
        print("\n⏹️  Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()