#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для Telegram бота
"""

import os
from typing import Optional

class Config:
    """Класс конфигурации бота"""
    
    # Токен бота (обязательно)
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Настройки базы данных
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'receipts.db')
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE')
    
    # Настройки временных файлов
    TEMP_DIR: str = os.getenv('TEMP_DIR', '/tmp')
    
    # Максимальный размер фото (в байтах)
    MAX_PHOTO_SIZE: int = int(os.getenv('MAX_PHOTO_SIZE', '20971520'))  # 20MB
    
    # Таймаут обработки фото (в секундах)
    PHOTO_TIMEOUT: int = int(os.getenv('PHOTO_TIMEOUT', '30'))
    
    @classmethod
    def validate(cls) -> bool:
        """Проверка корректности конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен. Установите переменную окружения BOT_TOKEN")
        return True