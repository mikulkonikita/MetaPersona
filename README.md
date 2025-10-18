# 🤖 Telegram Bot для сканирования чеков

Telegram бот для сканирования QR-кодов чеков, извлечения данных и сохранения в Google Таблицы.

## ✨ Возможности

- 📷 Сканирование QR-кодов чеков через камеру смартфона
- 🔍 Автоматическое извлечение данных из QR-кода:
  - Дата и время чека
  - Сумма чека
  - ФН, ФД, ФП чека
  - ИНН продавца
- 📊 Сохранение данных в Google Таблицы
- 🔒 Проверка на дубликаты чеков
- 📈 Статистика по чекам
- 🎯 Простой и интуитивный интерфейс

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/receipt-bot.git
cd receipt-bot
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
# Копирование файла конфигурации
cp .env.example .env

# Редактирование файла .env
nano .env
```

Заполните переменные в файле `.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_WORKSHEET_NAME=Receipts
```

### 4. Запуск бота

```bash
python run.py
```

## 📋 Подробная инструкция

Для подробной инструкции по настройке и развертыванию см. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🛠️ Технологии

- **Python 3.11+**
- **python-telegram-bot** - Telegram Bot API
- **OpenCV + pyzbar** - Распознавание QR-кодов
- **Google Sheets API** - Работа с таблицами
- **Docker** - Контейнеризация

## 📁 Структура проекта

```
receipt-bot/
├── main.py                    # Основной файл бота
├── qr_scanner.py             # Модуль сканирования QR-кодов
├── receipt_parser.py         # Модуль парсинга данных чека
├── google_sheets_manager.py  # Модуль работы с Google Sheets
├── config.py                 # Конфигурация
├── requirements.txt          # Зависимости Python
├── .env.example             # Пример файла переменных окружения
├── Dockerfile               # Docker конфигурация
├── docker-compose.yml       # Docker Compose конфигурация
├── run.py                   # Скрипт запуска
├── test_bot.py              # Тестовый скрипт
└── DEPLOYMENT_GUIDE.md      # Подробная инструкция
```

## 🧪 Тестирование

```bash
# Запуск тестов
python test_bot.py

# Проверка конфигурации
python run.py
```

## 🐳 Развертывание с Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 📊 Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/my_receipts` - Показать мои чеки
- `/stats` - Статистика по чекам

## 🔧 Настройка

### Создание Telegram бота

1. Найдите `@BotFather` в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

### Настройка Google Sheets

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API и Google Drive API
3. Создайте сервисный аккаунт
4. Скачайте JSON ключ
5. Создайте Google Таблицу
6. Поделитесь таблицей с email сервисного аккаунта

## 📝 Лицензия

Этот проект использует только бесплатные библиотеки, подходящие для коммерческого использования.

## 🤝 Поддержка

Если у вас возникли проблемы:

1. Проверьте [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Запустите тесты: `python test_bot.py`
3. Проверьте логи бота
4. Убедитесь, что все переменные окружения настроены

## 🔄 Обновление

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

---

**Создано с ❤️ для удобного сканирования чеков**