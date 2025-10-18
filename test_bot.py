#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы бота
"""

import os
import sys
import logging
from qr_parser import ReceiptQRParser
from database import ReceiptDatabase
from config import Config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qr_parser():
    """Тестирование парсера QR-кодов"""
    print("🔍 Тестирование парсера QR-кодов...")
    
    parser = ReceiptQRParser()
    
    # Тестовые QR-коды
    test_qrs = [
        "t=20231201T1430&s=150000&fn=1234567890&i=123&fp=456789&n=1",
        "t=20231201T1430&s=150000&fn=1234567890&i=123&fp=456789&n=1&inn=1234567890",
        "t=20231201T1430&s=150000&fn=1234567890&i=123&fp=456789&n=1&inn=1234567890&org=ООО Тест",
    ]
    
    for i, qr_data in enumerate(test_qrs, 1):
        print(f"\n📱 Тест QR-кода {i}:")
        print(f"   Входные данные: {qr_data}")
        
        result = parser.parse_qr_code(qr_data)
        if result:
            print(f"   ✅ Результат: {result}")
            
            # Валидация
            if parser.validate_receipt_data(result):
                print("   ✅ Валидация пройдена")
            else:
                print("   ❌ Валидация не пройдена")
        else:
            print("   ❌ Ошибка парсинга")
    
    print("\n✅ Тестирование парсера завершено")

def test_database():
    """Тестирование базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    try:
        # Создаем тестовую базу данных
        test_db_path = "test_receipts.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db = ReceiptDatabase(test_db_path)
        print("   ✅ База данных создана")
        
        # Тестовые данные
        test_receipt = {
            'receipt_date': '2023-12-01',
            'receipt_time': '14:30',
            'total_amount': 1500.0,
            'fn_number': '1234567890',
            'fd_number': '123',
            'fp_number': '456789',
            'seller_inn': '1234567890'
        }
        
        # Тест сохранения
        success = db.save_receipt(12345, test_receipt)
        if success:
            print("   ✅ Чек сохранен")
        else:
            print("   ❌ Ошибка сохранения чека")
        
        # Тест проверки дубликатов
        success2 = db.save_receipt(12345, test_receipt)
        if not success2:
            print("   ✅ Дубликат корректно обнаружен")
        else:
            print("   ❌ Дубликат не обнаружен")
        
        # Тест получения статистики
        stats = db.get_user_stats(12345)
        if stats and stats['total_receipts'] == 1:
            print("   ✅ Статистика корректна")
        else:
            print("   ❌ Ошибка статистики")
        
        # Очистка
        os.remove(test_db_path)
        print("   ✅ Тестовая база данных удалена")
        
    except Exception as e:
        print(f"   ❌ Ошибка тестирования базы данных: {e}")
    
    print("\n✅ Тестирование базы данных завершено")

def test_config():
    """Тестирование конфигурации"""
    print("\n⚙️ Тестирование конфигурации...")
    
    try:
        # Проверяем валидацию конфигурации
        Config.validate()
        print("   ✅ Конфигурация валидна")
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
    
    print("\n✅ Тестирование конфигурации завершено")

def test_dependencies():
    """Тестирование зависимостей"""
    print("\n📦 Тестирование зависимостей...")
    
    dependencies = [
        ('telegram', 'python-telegram-bot'),
        ('PIL', 'Pillow'),
        ('pyzbar', 'pyzbar'),
        ('qrcode', 'qrcode'),
        ('sqlite3', 'sqlite3'),
    ]
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - не установлен")
    
    print("\n✅ Тестирование зависимостей завершено")

def main():
    """Главная функция тестирования"""
    print("🧪 Запуск тестов Telegram бота для сканирования чеков\n")
    
    # Тестируем зависимости
    test_dependencies()
    
    # Тестируем конфигурацию
    test_config()
    
    # Тестируем парсер QR-кодов
    test_qr_parser()
    
    # Тестируем базу данных
    test_database()
    
    print("\n🎉 Все тесты завершены!")
    print("\n📋 Для запуска бота выполните:")
    print("   python main.py")
    print("\n📋 Для получения справки:")
    print("   python admin.py")

if __name__ == '__main__':
    main()