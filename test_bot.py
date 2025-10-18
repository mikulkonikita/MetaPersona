#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы бота
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_imports():
    """Тест импортов"""
    print("🔍 Проверка импортов...")
    
    try:
        from qr_scanner import QRCodeScanner
        print("✅ QRCodeScanner импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта QRCodeScanner: {e}")
        return False
    
    try:
        from receipt_parser import ReceiptParser
        print("✅ ReceiptParser импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта ReceiptParser: {e}")
        return False
    
    try:
        from google_sheets_manager import GoogleSheetsManager
        print("✅ GoogleSheetsManager импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта GoogleSheetsManager: {e}")
        return False
    
    return True

def test_qr_parser():
    """Тест парсера QR-кодов"""
    print("\n🔍 Тестирование парсера QR-кодов...")
    
    try:
        from receipt_parser import ReceiptParser
        parser = ReceiptParser()
        
        # Тестовый QR-код
        test_qr = "t=20231215T143000&s=1500.00&fn=1234567890&fd=123&fp=4567890123&i=123456789012"
        
        result = parser.parse_receipt_qr(test_qr)
        
        if result:
            print("✅ Парсинг QR-кода работает")
            print(f"   Извлеченные данные: {len(result)} полей")
            return True
        else:
            print("❌ Парсинг QR-кода не работает")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования парсера: {e}")
        return False

def test_google_sheets():
    """Тест подключения к Google Sheets"""
    print("\n🔍 Тестирование подключения к Google Sheets...")
    
    try:
        from google_sheets_manager import GoogleSheetsManager
        
        credentials = os.getenv('GOOGLE_CREDENTIALS_JSON')
        spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        
        if not credentials or not spreadsheet_id:
            print("⚠️  Переменные Google Sheets не настроены, пропускаем тест")
            return True
        
        manager = GoogleSheetsManager(credentials, spreadsheet_id)
        
        if manager.is_connected():
            print("✅ Подключение к Google Sheets работает")
            return True
        else:
            print("❌ Подключение к Google Sheets не работает")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования Google Sheets: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование компонентов бота")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_qr_parser,
        test_google_sheets
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✅ Все тесты пройдены успешно!")
        return True
    else:
        print("❌ Некоторые тесты не пройдены")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)