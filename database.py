#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных
"""

import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ReceiptDatabase:
    """Класс для работы с базой данных чеков"""
    
    def __init__(self, db_path: str = 'receipts.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу чеков
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS receipts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        scan_date TEXT NOT NULL,
                        receipt_date TEXT,
                        receipt_time TEXT,
                        total_amount REAL,
                        fn_number TEXT,
                        fd_number TEXT,
                        fp_number TEXT,
                        seller_inn TEXT,
                        qr_hash TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Создаем индексы для быстрого поиска
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id ON receipts(user_id)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_qr_hash ON receipts(qr_hash)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_scan_date ON receipts(scan_date)
                ''')
                
                conn.commit()
                logger.info("База данных инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def generate_qr_hash(self, fn_number: str, fd_number: str, fp_number: str) -> str:
        """Генерация хеша для проверки дубликатов"""
        unique_string = f"{fn_number or ''}{fd_number or ''}{fp_number or ''}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def check_receipt_exists(self, qr_hash: str) -> bool:
        """Проверка существования чека"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM receipts WHERE qr_hash = ?', (qr_hash,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка проверки существования чека: {e}")
            return False
    
    def save_receipt(self, user_id: int, receipt_data: Dict[str, Any]) -> bool:
        """Сохранение чека в базу данных"""
        try:
            # Генерируем хеш для проверки дубликатов
            qr_hash = self.generate_qr_hash(
                receipt_data.get('fn_number', ''),
                receipt_data.get('fd_number', ''),
                receipt_data.get('fp_number', '')
            )
            
            # Проверяем, существует ли уже такой чек
            if self.check_receipt_exists(qr_hash):
                return False
            
            # Сохраняем новый чек
            scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO receipts 
                    (user_id, scan_date, receipt_date, receipt_time, total_amount, 
                     fn_number, fd_number, fp_number, seller_inn, qr_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, scan_date, receipt_data.get('receipt_date'),
                    receipt_data.get('receipt_time'), receipt_data.get('total_amount'),
                    receipt_data.get('fn_number'), receipt_data.get('fd_number'),
                    receipt_data.get('fp_number'), receipt_data.get('seller_inn'), qr_hash
                ))
                conn.commit()
            
            logger.info(f"Чек сохранен для пользователя {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения чека: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение статистики пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as total_receipts,
                           COALESCE(SUM(total_amount), 0) as total_amount,
                           MIN(scan_date) as first_scan,
                           MAX(scan_date) as last_scan
                    FROM receipts 
                    WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'total_receipts': result[0],
                        'total_amount': result[1],
                        'first_scan': result[2],
                        'last_scan': result[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return None
    
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Dict[str, Any]]:
        """Получение чека по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, scan_date, receipt_date, receipt_time,
                           total_amount, fn_number, fd_number, fp_number, seller_inn
                    FROM receipts 
                    WHERE id = ?
                ''', (receipt_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'user_id': result[1],
                        'scan_date': result[2],
                        'receipt_date': result[3],
                        'receipt_time': result[4],
                        'total_amount': result[5],
                        'fn_number': result[6],
                        'fd_number': result[7],
                        'fp_number': result[8],
                        'seller_inn': result[9]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения чека: {e}")
            return None
    
    def get_user_receipts(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение чеков пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, scan_date, receipt_date, receipt_time, total_amount,
                           fn_number, fd_number, fp_number, seller_inn
                    FROM receipts 
                    WHERE user_id = ?
                    ORDER BY scan_date DESC
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
                
                results = cursor.fetchall()
                receipts = []
                for result in results:
                    receipts.append({
                        'id': result[0],
                        'scan_date': result[1],
                        'receipt_date': result[2],
                        'receipt_time': result[3],
                        'total_amount': result[4],
                        'fn_number': result[5],
                        'fd_number': result[6],
                        'fp_number': result[7],
                        'seller_inn': result[8]
                    })
                return receipts
                
        except Exception as e:
            logger.error(f"Ошибка получения чеков пользователя: {e}")
            return []
    
    def get_all_stats(self) -> Optional[Dict[str, Any]]:
        """Получение общей статистики"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as total_receipts,
                           COUNT(DISTINCT user_id) as unique_users,
                           COALESCE(SUM(total_amount), 0) as total_amount,
                           MIN(scan_date) as first_scan,
                           MAX(scan_date) as last_scan
                    FROM receipts
                ''')
                
                result = cursor.fetchone()
                if result:
                    return {
                        'total_receipts': result[0],
                        'unique_users': result[1],
                        'total_amount': result[1],
                        'first_scan': result[3],
                        'last_scan': result[4]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения общей статистики: {e}")
            return None