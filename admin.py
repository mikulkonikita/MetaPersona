#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Административный модуль для управления ботом
"""

import logging
import sys
from typing import List, Dict, Any
from database import ReceiptDatabase
from config import Config

logger = logging.getLogger(__name__)

class AdminPanel:
    """Панель администратора для управления ботом"""
    
    def __init__(self, db_path: str = None):
        self.db = ReceiptDatabase(db_path or Config.DATABASE_PATH)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получение общей статистики"""
        return self.db.get_all_stats()
    
    def get_user_receipts(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение чеков пользователя"""
        return self.db.get_user_receipts(user_id, limit)
    
    def get_receipt_by_id(self, receipt_id: int) -> Dict[str, Any]:
        """Получение чека по ID"""
        return self.db.get_receipt_by_id(receipt_id)
    
    def export_receipts_csv(self, filename: str = 'receipts_export.csv'):
        """Экспорт чеков в CSV"""
        import csv
        import sqlite3
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, scan_date, receipt_date, receipt_time, 
                           total_amount, fn_number, fd_number, fp_number, seller_inn
                    FROM receipts 
                    ORDER BY scan_date DESC
                ''')
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        'User ID', 'Scan Date', 'Receipt Date', 'Receipt Time',
                        'Total Amount', 'FN Number', 'FD Number', 'FP Number', 'Seller INN'
                    ])
                    
                    for row in cursor.fetchall():
                        writer.writerow(row)
                
                print(f"✅ Данные экспортированы в {filename}")
                
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
    
    def cleanup_old_receipts(self, days: int = 30):
        """Очистка старых чеков"""
        import sqlite3
        from datetime import datetime, timedelta
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM receipts WHERE scan_date < ?', (cutoff_date,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    cursor.execute('DELETE FROM receipts WHERE scan_date < ?', (cutoff_date,))
                    conn.commit()
                    print(f"✅ Удалено {count} чеков старше {days} дней")
                else:
                    print("ℹ️ Нет чеков для удаления")
                    
        except Exception as e:
            print(f"❌ Ошибка очистки: {e}")

def main():
    """Главная функция административной панели"""
    if len(sys.argv) < 2:
        print("""
🤖 Административная панель бота сканирования чеков

Использование:
    python admin.py stats                    - Показать общую статистику
    python admin.py user <user_id>          - Показать чеки пользователя
    python admin.py receipt <receipt_id>    - Показать чек по ID
    python admin.py export [filename]       - Экспорт в CSV
    python admin.py cleanup [days]          - Очистка старых чеков
        """)
        return
    
    admin = AdminPanel()
    command = sys.argv[1]
    
    if command == 'stats':
        stats = admin.get_all_stats()
        if stats:
            print(f"""
📊 Общая статистика:
   📄 Всего чеков: {stats['total_receipts']}
   👥 Уникальных пользователей: {stats['unique_users']}
   💰 Общая сумма: {stats['total_amount']:.2f} ₽
   📅 Первый чек: {stats['first_scan']}
   📅 Последний чек: {stats['last_scan']}
            """)
        else:
            print("📊 Нет данных для отображения")
    
    elif command == 'user':
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя")
            return
        
        user_id = int(sys.argv[2])
        receipts = admin.get_user_receipts(user_id, 20)
        
        if receipts:
            print(f"\n📄 Чеки пользователя {user_id}:")
            for receipt in receipts:
                print(f"   ID: {receipt['id']} | {receipt['scan_date']} | {receipt['total_amount']:.2f} ₽")
        else:
            print(f"📄 У пользователя {user_id} нет чеков")
    
    elif command == 'receipt':
        if len(sys.argv) < 3:
            print("❌ Укажите ID чека")
            return
        
        receipt_id = int(sys.argv[2])
        receipt = admin.get_receipt_by_id(receipt_id)
        
        if receipt:
            print(f"""
📄 Чек ID {receipt_id}:
   👤 Пользователь: {receipt['user_id']}
   📅 Дата сканирования: {receipt['scan_date']}
   📅 Дата чека: {receipt['receipt_date']}
   🕐 Время чека: {receipt['receipt_time']}
   💰 Сумма: {receipt['total_amount']:.2f} ₽
   🏪 ИНН продавца: {receipt['seller_inn']}
   📋 ФН: {receipt['fn_number']}
   📋 ФД: {receipt['fd_number']}
   📋 ФП: {receipt['fp_number']}
            """)
        else:
            print(f"❌ Чек с ID {receipt_id} не найден")
    
    elif command == 'export':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'receipts_export.csv'
        admin.export_receipts_csv(filename)
    
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        admin.cleanup_old_receipts(days)
    
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == '__main__':
    main()