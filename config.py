import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')
GOOGLE_WORKSHEET_NAME = os.getenv('GOOGLE_WORKSHEET_NAME', 'Receipts')

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Настройки Google Sheets
SHEET_HEADERS = [
    'ID пользователя', 'Дата сканирования', 'Дата чека', 'Время чека',
    'Сумма чека', 'ФН чека', 'ФД чека', 'ФП чека', 'ИНН продавца',
    'Сырой QR код', 'Статус'
]

# Настройки парсинга QR-кодов
QR_PATTERNS = {
    'date': r't=(\d{8})',
    'time': r't=(\d{8})T(\d{6})',
    'sum': r's=([\d.]+)',
    'fn': r'fn=(\d+)',
    'fd': r'fd=(\d+)',
    'fp': r'fp=(\d+)',
    'inn': r'i=(\d+)',
}

# Обязательные поля для валидации чека
REQUIRED_FIELDS = ['fn', 'fd', 'fp', 'sum']