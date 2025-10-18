import re
import logging
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ReceiptParser:
    """Класс для парсинга данных из QR-кодов чеков"""
    
    def __init__(self):
        # Паттерны для извлечения данных из QR-кода чека
        self.patterns = {
            'date': r't=(\d{8})',  # Дата в формате YYYYMMDD
            'time': r't=(\d{8})T(\d{6})',  # Время в формате YYYYMMDDTHHMMSS
            'sum': r's=([\d.]+)',  # Сумма чека
            'fn': r'fn=(\d+)',  # ФН (фискальный номер)
            'fd': r'fd=(\d+)',  # ФД (фискальный документ)
            'fp': r'fp=(\d+)',  # ФП (фискальный признак)
            'inn': r'i=(\d+)',  # ИНН продавца
            'n': r'n=(\d+)',  # Номер чека
            'tax_system': r'tax=(\d+)',  # Система налогообложения
            'operation_type': r'op=(\d+)',  # Тип операции
        }
        
        # Обязательные поля для валидации чека
        self.required_fields = ['fn', 'fd', 'fp', 'sum']
    
    def clean_qr_text(self, qr_text: str) -> str:
        """Очистка текста QR-кода от лишних символов"""
        if not qr_text:
            return ""
        
        # Убираем лишние пробелы и переносы строк
        cleaned = qr_text.strip()
        
        # Убираем возможные артефакты
        cleaned = re.sub(r'[^\w\s=.-]', '', cleaned)
        
        return cleaned
    
    def extract_date_time(self, qr_text: str) -> Dict[str, str]:
        """Извлечение даты и времени из QR-кода"""
        result = {}
        
        try:
            # Ищем полный формат даты и времени
            time_match = re.search(self.patterns['time'], qr_text)
            if time_match:
                date_str = time_match.group(1)
                time_str = time_match.group(2)
                
                # Форматируем дату
                result['date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                
                # Форматируем время
                result['time'] = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                # Пробуем найти только дату
                date_match = re.search(self.patterns['date'], qr_text)
                if date_match:
                    date_str = date_match.group(1)
                    result['date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    result['time'] = ""
        except Exception as e:
            logger.error(f"Ошибка извлечения даты и времени: {e}")
        
        return result
    
    def extract_financial_data(self, qr_text: str) -> Dict[str, str]:
        """Извлечение финансовых данных из QR-кода"""
        result = {}
        
        try:
            # Извлекаем сумму
            sum_match = re.search(self.patterns['sum'], qr_text)
            if sum_match:
                result['sum'] = sum_match.group(1)
            
            # Извлекаем ФН
            fn_match = re.search(self.patterns['fn'], qr_text)
            if fn_match:
                result['fn'] = fn_match.group(1)
            
            # Извлекаем ФД
            fd_match = re.search(self.patterns['fd'], qr_text)
            if fd_match:
                result['fd'] = fd_match.group(1)
            
            # Извлекаем ФП
            fp_match = re.search(self.patterns['fp'], qr_text)
            if fp_match:
                result['fp'] = fp_match.group(1)
            
            # Извлекаем ИНН
            inn_match = re.search(self.patterns['inn'], qr_text)
            if inn_match:
                result['inn'] = inn_match.group(1)
            
            # Извлекаем номер чека
            n_match = re.search(self.patterns['n'], qr_text)
            if n_match:
                result['n'] = n_match.group(1)
            
            # Извлекаем систему налогообложения
            tax_match = re.search(self.patterns['tax_system'], qr_text)
            if tax_match:
                result['tax_system'] = tax_match.group(1)
            
            # Извлекаем тип операции
            op_match = re.search(self.patterns['operation_type'], qr_text)
            if op_match:
                result['operation_type'] = op_match.group(1)
                
        except Exception as e:
            logger.error(f"Ошибка извлечения финансовых данных: {e}")
        
        return result
    
    def validate_receipt_data(self, receipt_data: Dict[str, str]) -> List[str]:
        """Валидация данных чека"""
        errors = []
        
        # Проверяем наличие обязательных полей
        for field in self.required_fields:
            if field not in receipt_data or not receipt_data[field]:
                errors.append(f"Отсутствует обязательное поле: {field}")
        
        # Проверяем формат суммы
        if 'sum' in receipt_data and receipt_data['sum']:
            try:
                sum_value = float(receipt_data['sum'])
                if sum_value <= 0:
                    errors.append("Сумма чека должна быть больше 0")
            except ValueError:
                errors.append("Неверный формат суммы чека")
        
        # Проверяем формат даты
        if 'date' in receipt_data and receipt_data['date']:
            try:
                datetime.strptime(receipt_data['date'], '%Y-%m-%d')
            except ValueError:
                errors.append("Неверный формат даты чека")
        
        # Проверяем формат времени
        if 'time' in receipt_data and receipt_data['time']:
            try:
                datetime.strptime(receipt_data['time'], '%H:%M:%S')
            except ValueError:
                errors.append("Неверный формат времени чека")
        
        return errors
    
    def parse_receipt_qr(self, qr_text: str) -> Dict[str, str]:
        """Основной метод парсинга QR-кода чека"""
        try:
            # Очищаем текст
            cleaned_qr = self.clean_qr_text(qr_text)
            
            if not cleaned_qr:
                logger.warning("Пустой QR-код")
                return {}
            
            # Извлекаем данные
            result = {}
            
            # Извлекаем дату и время
            date_time_data = self.extract_date_time(cleaned_qr)
            result.update(date_time_data)
            
            # Извлекаем финансовые данные
            financial_data = self.extract_financial_data(cleaned_qr)
            result.update(financial_data)
            
            # Добавляем сырой QR-код для отладки
            result['raw_qr'] = cleaned_qr
            
            # Валидируем данные
            validation_errors = self.validate_receipt_data(result)
            if validation_errors:
                logger.warning(f"Ошибки валидации: {validation_errors}")
                result['validation_errors'] = validation_errors
            
            logger.info(f"Успешно распарсен QR-код: {len(result)} полей")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка парсинга QR-кода: {e}")
            return {}
    
    def is_valid_receipt(self, receipt_data: Dict[str, str]) -> bool:
        """Проверка валидности данных чека"""
        validation_errors = self.validate_receipt_data(receipt_data)
        return len(validation_errors) == 0
    
    def get_receipt_summary(self, receipt_data: Dict[str, str]) -> str:
        """Получение краткой сводки по чеку"""
        if not receipt_data:
            return "Данные чека не найдены"
        
        summary_parts = []
        
        if 'date' in receipt_data and receipt_data['date']:
            summary_parts.append(f"Дата: {receipt_data['date']}")
        
        if 'time' in receipt_data and receipt_data['time']:
            summary_parts.append(f"Время: {receipt_data['time']}")
        
        if 'sum' in receipt_data and receipt_data['sum']:
            summary_parts.append(f"Сумма: {receipt_data['sum']} руб.")
        
        if 'fn' in receipt_data and receipt_data['fn']:
            summary_parts.append(f"ФН: {receipt_data['fn']}")
        
        if 'fd' in receipt_data and receipt_data['fd']:
            summary_parts.append(f"ФД: {receipt_data['fd']}")
        
        if 'fp' in receipt_data and receipt_data['fp']:
            summary_parts.append(f"ФП: {receipt_data['fp']}")
        
        if 'inn' in receipt_data and receipt_data['inn']:
            summary_parts.append(f"ИНН: {receipt_data['inn']}")
        
        return "\n".join(summary_parts) if summary_parts else "Нет данных для отображения"