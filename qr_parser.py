#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для парсинга QR-кодов чеков
"""

import re
import urllib.parse
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ReceiptQRParser:
    """Класс для парсинга QR-кодов чеков"""
    
    def __init__(self):
        # Регулярные выражения для различных форматов QR-кодов
        self.patterns = {
            'fiscal': r't=(\d{8}T\d{4})&s=([\d.]+)&fn=(\d+)&i=(\d+)&fp=(\d+)&n=(\d+)',
            'fiscal_with_inn': r't=(\d{8}T\d{4})&s=([\d.]+)&fn=(\d+)&i=(\d+)&fp=(\d+)&n=(\d+)&inn=(\d+)',
            'extended': r't=(\d{8}T\d{4})&s=([\d.]+)&fn=(\d+)&i=(\d+)&fp=(\d+)&n=(\d+)&inn=(\d+)&org=([^&]+)',
        }
    
    def parse_qr_code(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг QR-кода чека
        Поддерживает различные форматы QR-кодов
        """
        try:
            # Декодируем URL-encoded строку
            decoded_data = urllib.parse.unquote(qr_data)
            logger.info(f"Декодированные данные QR-кода: {decoded_data}")
            
            # Пытаемся найти подходящий паттерн
            for pattern_name, pattern in self.patterns.items():
                match = re.search(pattern, decoded_data)
                if match:
                    return self._parse_by_pattern(pattern_name, match, decoded_data)
            
            # Если не нашли по паттерну, пытаемся парсить вручную
            return self._parse_manual(decoded_data)
            
        except Exception as e:
            logger.error(f"Ошибка парсинга QR-кода: {e}")
            return None
    
    def _parse_by_pattern(self, pattern_name: str, match: re.Match, decoded_data: str) -> Dict[str, Any]:
        """Парсинг по найденному паттерну"""
        groups = match.groups()
        
        if pattern_name == 'fiscal':
            return self._parse_fiscal_pattern(groups, decoded_data)
        elif pattern_name == 'fiscal_with_inn':
            return self._parse_fiscal_with_inn_pattern(groups, decoded_data)
        elif pattern_name == 'extended':
            return self._parse_extended_pattern(groups, decoded_data)
        
        return self._parse_manual(decoded_data)
    
    def _parse_fiscal_pattern(self, groups: tuple, decoded_data: str) -> Dict[str, Any]:
        """Парсинг базового фискального паттерна"""
        date_time_str, amount_str, fn_number, fd_number, fp_number, operation_type = groups
        
        return {
            'receipt_date': self._parse_date(date_time_str),
            'receipt_time': self._parse_time(date_time_str),
            'total_amount': self._parse_amount(amount_str),
            'fn_number': fn_number,
            'fd_number': fd_number,
            'fp_number': fp_number,
            'operation_type': operation_type,
            'seller_inn': self._extract_inn_from_params(decoded_data),
            'raw_data': decoded_data
        }
    
    def _parse_fiscal_with_inn_pattern(self, groups: tuple, decoded_data: str) -> Dict[str, Any]:
        """Парсинг фискального паттерна с ИНН"""
        date_time_str, amount_str, fn_number, fd_number, fp_number, operation_type, seller_inn = groups
        
        return {
            'receipt_date': self._parse_date(date_time_str),
            'receipt_time': self._parse_time(date_time_str),
            'total_amount': self._parse_amount(amount_str),
            'fn_number': fn_number,
            'fd_number': fd_number,
            'fp_number': fp_number,
            'operation_type': operation_type,
            'seller_inn': seller_inn,
            'raw_data': decoded_data
        }
    
    def _parse_extended_pattern(self, groups: tuple, decoded_data: str) -> Dict[str, Any]:
        """Парсинг расширенного паттерна"""
        date_time_str, amount_str, fn_number, fd_number, fp_number, operation_type, seller_inn, org_name = groups
        
        return {
            'receipt_date': self._parse_date(date_time_str),
            'receipt_time': self._parse_time(date_time_str),
            'total_amount': self._parse_amount(amount_str),
            'fn_number': fn_number,
            'fd_number': fd_number,
            'fp_number': fp_number,
            'operation_type': operation_type,
            'seller_inn': seller_inn,
            'org_name': org_name,
            'raw_data': decoded_data
        }
    
    def _parse_manual(self, decoded_data: str) -> Dict[str, Any]:
        """Ручной парсинг параметров"""
        params = {}
        for param in decoded_data.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        # Парсим дату и время
        date_time_str = params.get('t', '')
        receipt_date, receipt_time = self._parse_date_time(date_time_str)
        
        # Парсим сумму
        total_amount = self._parse_amount(params.get('s', '0'))
        
        return {
            'receipt_date': receipt_date,
            'receipt_time': receipt_time,
            'total_amount': total_amount,
            'fn_number': params.get('fn'),
            'fd_number': params.get('i'),
            'fp_number': params.get('fp'),
            'operation_type': params.get('n'),
            'seller_inn': params.get('inn') or self._extract_inn_from_params(decoded_data),
            'org_name': params.get('org'),
            'raw_data': decoded_data
        }
    
    def _parse_date_time(self, date_time_str: str) -> tuple:
        """Парсинг даты и времени из строки формата YYYYMMDDThhmm"""
        if len(date_time_str) >= 15:
            try:
                # Формат: YYYYMMDDThhmm
                date_part = date_time_str[:8]  # YYYYMMDD
                time_part = date_time_str[9:13]  # hhmm
                
                # Преобразуем дату
                year = int(date_part[:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                receipt_date = f"{year:04d}-{month:02d}-{day:02d}"
                
                # Преобразуем время
                hour = int(time_part[:2])
                minute = int(time_part[2:4])
                receipt_time = f"{hour:02d}:{minute:02d}"
                
                return receipt_date, receipt_time
            except (ValueError, IndexError):
                pass
        
        return None, None
    
    def _parse_date(self, date_time_str: str) -> Optional[str]:
        """Парсинг только даты"""
        date, _ = self._parse_date_time(date_time_str)
        return date
    
    def _parse_time(self, date_time_str: str) -> Optional[str]:
        """Парсинг только времени"""
        _, time = self._parse_date_time(date_time_str)
        return time
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Парсинг суммы (в копейках)"""
        try:
            # Убираем все нецифровые символы кроме точки
            clean_amount = re.sub(r'[^\d.]', '', amount_str)
            if clean_amount:
                # Конвертируем копейки в рубли
                return float(clean_amount) / 100
        except (ValueError, TypeError):
            pass
        return None
    
    def _extract_inn_from_params(self, decoded_data: str) -> Optional[str]:
        """Извлечение ИНН из параметров"""
        # Ищем параметры, которые могут содержать ИНН
        inn_patterns = [
            r'inn=(\d{10,12})',
            r'n=(\d{10,12})',
            r'org=(\d{10,12})',
        ]
        
        for pattern in inn_patterns:
            match = re.search(pattern, decoded_data)
            if match:
                inn = match.group(1)
                if len(inn) in [10, 12] and inn.isdigit():
                    return inn
        
        return None
    
    def validate_receipt_data(self, receipt_data: Dict[str, Any]) -> bool:
        """Валидация данных чека"""
        required_fields = ['fn_number', 'fd_number', 'fp_number']
        
        # Проверяем наличие обязательных полей
        for field in required_fields:
            if not receipt_data.get(field):
                logger.warning(f"Отсутствует обязательное поле: {field}")
                return False
        
        # Проверяем формат ФН (должен быть числом)
        if not receipt_data.get('fn_number', '').isdigit():
            logger.warning("ФН должен быть числом")
            return False
        
        # Проверяем формат ФД (должен быть числом)
        if not receipt_data.get('fd_number', '').isdigit():
            logger.warning("ФД должен быть числом")
            return False
        
        # Проверяем формат ФП (должен быть числом)
        if not receipt_data.get('fp_number', '').isdigit():
            logger.warning("ФП должен быть числом")
            return False
        
        return True