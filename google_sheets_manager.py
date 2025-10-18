import gspread
from google.oauth2.service_account import Credentials
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Класс для работы с Google Sheets"""
    
    def __init__(self, credentials_json: str, spreadsheet_id: str, worksheet_name: str = "Receipts"):
        self.credentials_json = credentials_json
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.gc = None
        self.worksheet = None
        self.headers = [
            'ID пользователя', 'Дата сканирования', 'Дата чека', 'Время чека',
            'Сумма чека', 'ФН чека', 'ФД чека', 'ФП чека', 'ИНН продавца',
            'Сырой QR код', 'Статус'
        ]
        
        self._init_connection()
    
    def _init_connection(self):
        """Инициализация подключения к Google Sheets"""
        try:
            if not self.credentials_json:
                logger.error("Google credentials не предоставлены")
                return False
            
            # Парсим JSON из строки
            creds_info = json.loads(self.credentials_json)
            
            # Настраиваем области доступа
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Создаем credentials
            credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
            
            # Авторизуемся
            self.gc = gspread.authorize(credentials)
            
            # Открываем таблицу
            if self.spreadsheet_id:
                spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
                
                # Получаем или создаем лист
                try:
                    self.worksheet = spreadsheet.worksheet(self.worksheet_name)
                    logger.info(f"Лист '{self.worksheet_name}' найден")
                except gspread.WorksheetNotFound:
                    logger.info(f"Лист '{self.worksheet_name}' не найден, создаем новый")
                    self.worksheet = spreadsheet.add_worksheet(
                        title=self.worksheet_name, 
                        rows=1000, 
                        cols=len(self.headers)
                    )
                    # Добавляем заголовки
                    self.worksheet.append_row(self.headers)
                    logger.info("Заголовки добавлены")
                
                logger.info("Google Sheets подключение успешно инициализировано")
                return True
            else:
                logger.error("Spreadsheet ID не предоставлен")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON credentials: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Sheets: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Проверка подключения к Google Sheets"""
        return self.gc is not None and self.worksheet is not None
    
    def check_duplicate_receipt(self, fn: str, fd: str, fp: str) -> bool:
        """Проверка на дубликат чека по ФН, ФД, ФП"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return False
            
            # Получаем все записи
            records = self.worksheet.get_all_records()
            
            for record in records:
                if (record.get('ФН чека') == str(fn) and 
                    record.get('ФД чека') == str(fd) and 
                    record.get('ФП чека') == str(fp)):
                    logger.info(f"Найден дубликат чека: ФН={fn}, ФД={fd}, ФП={fp}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки дубликата: {e}")
            return False
    
    def save_receipt(self, user_id: int, qr_text: str, receipt_data: Dict[str, str]) -> bool:
        """Сохранение данных чека в Google Sheets"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return False
            
            # Подготавливаем данные для записи
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row_data = [
                str(user_id),  # ID пользователя
                current_time,  # Дата сканирования
                receipt_data.get('date', ''),  # Дата чека
                receipt_data.get('time', ''),  # Время чека
                receipt_data.get('sum', ''),  # Сумма чека
                receipt_data.get('fn', ''),  # ФН чека
                receipt_data.get('fd', ''),  # ФД чека
                receipt_data.get('fp', ''),  # ФП чека
                receipt_data.get('inn', ''),  # ИНН продавца
                qr_text,  # Сырой QR код
                'Принят'  # Статус
            ]
            
            # Добавляем строку
            self.worksheet.append_row(row_data)
            
            logger.info(f"Чек сохранен для пользователя {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в Google Sheets: {e}")
            return False
    
    def get_user_receipts(self, user_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Получение чеков пользователя"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return []
            
            # Получаем все записи
            records = self.worksheet.get_all_records()
            
            # Фильтруем по пользователю
            user_records = [
                record for record in records 
                if record.get('ID пользователя') == str(user_id)
            ]
            
            # Сортируем по дате сканирования (новые сначала)
            user_records.sort(
                key=lambda x: x.get('Дата сканирования', ''), 
                reverse=True
            )
            
            return user_records[:limit]
            
        except Exception as e:
            logger.error(f"Ошибка получения чеков пользователя: {e}")
            return []
    
    def get_receipt_statistics(self) -> Dict[str, int]:
        """Получение статистики по чекам"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return {}
            
            # Получаем все записи
            records = self.worksheet.get_all_records()
            
            # Подсчитываем статистику
            total_receipts = len(records)
            unique_users = len(set(record.get('ID пользователя', '') for record in records))
            
            # Подсчитываем по статусам
            status_counts = {}
            for record in records:
                status = record.get('Статус', 'Неизвестно')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_receipts': total_receipts,
                'unique_users': unique_users,
                'status_counts': status_counts
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def search_receipts(self, search_criteria: Dict[str, str]) -> List[Dict[str, str]]:
        """Поиск чеков по критериям"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return []
            
            # Получаем все записи
            records = self.worksheet.get_all_records()
            
            # Фильтруем по критериям
            filtered_records = []
            for record in records:
                match = True
                for key, value in search_criteria.items():
                    if key in record and record[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_records.append(record)
            
            return filtered_records
            
        except Exception as e:
            logger.error(f"Ошибка поиска чеков: {e}")
            return []
    
    def update_receipt_status(self, fn: str, fd: str, fp: str, new_status: str) -> bool:
        """Обновление статуса чека"""
        try:
            if not self.is_connected():
                logger.error("Нет подключения к Google Sheets")
                return False
            
            # Находим строку с чеком
            records = self.worksheet.get_all_records()
            for i, record in enumerate(records, start=2):  # Начинаем с 2, так как 1 - заголовки
                if (record.get('ФН чека') == str(fn) and 
                    record.get('ФД чека') == str(fd) and 
                    record.get('ФП чека') == str(fp)):
                    
                    # Обновляем статус
                    self.worksheet.update_cell(i, 11, new_status)  # 11 - колонка "Статус"
                    logger.info(f"Статус чека обновлен: {new_status}")
                    return True
            
            logger.warning(f"Чек не найден: ФН={fn}, ФД={fd}, ФП={fp}")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обновления статуса чека: {e}")
            return False