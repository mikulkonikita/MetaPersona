# 📋 Подробная инструкция по развертыванию Telegram бота для сканирования чеков

## 🎯 Описание проекта

Этот бот позволяет пользователям сканировать QR-коды с чеков через камеру смартфона, извлекать из них данные (дата, время, сумма, ФН, ФД, ФП, ИНН продавца) и сохранять в Google Таблицы.

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
└── DEPLOYMENT_GUIDE.md      # Эта инструкция
```

## 🚀 Пошаговая инструкция по развертыванию

### Шаг 1: Создание Telegram бота

1. **Откройте Telegram** и найдите бота `@BotFather`
2. **Отправьте команду** `/newbot`
3. **Введите имя бота** (например: "Receipt Scanner Bot")
4. **Введите username бота** (например: "receipt_scanner_bot")
5. **Скопируйте токен** бота (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 2: Настройка Google Sheets

#### 2.1 Создание Google Cloud проекта

1. **Перейдите на** [Google Cloud Console](https://console.cloud.google.com/)
2. **Создайте новый проект** или выберите существующий
3. **Включите Google Sheets API:**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google Sheets API" и включите его
   - Найдите "Google Drive API" и включите его

#### 2.2 Создание сервисного аккаунта

1. **Перейдите в** "APIs & Services" → "Credentials"
2. **Нажмите** "Create Credentials" → "Service Account"
3. **Заполните данные:**
   - Name: `receipt-bot-service`
   - Description: `Service account for receipt bot`
4. **Нажмите** "Create and Continue"
5. **В разделе "Grant this service account access to project":**
   - Role: `Editor`
6. **Нажмите** "Done"

#### 2.3 Создание ключа сервисного аккаунта

1. **Найдите созданный сервисный аккаунт** в списке
2. **Нажмите на email** сервисного аккаунта
3. **Перейдите во вкладку** "Keys"
4. **Нажмите** "Add Key" → "Create new key"
5. **Выберите** "JSON" и нажмите "Create"
6. **Скачайте файл** и сохраните его как `service-account-key.json`

#### 2.4 Создание Google Таблицы

1. **Перейдите на** [Google Sheets](https://sheets.google.com/)
2. **Создайте новую таблицу**
3. **Дайте ей название** (например: "Receipts Database")
4. **Скопируйте ID таблицы** из URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
5. **Поделитесь таблицей** с email сервисного аккаунта:
   - Нажмите "Share" в правом верхнем углу
   - Введите email сервисного аккаунта (из файла JSON)
   - Выберите права "Editor"
   - Нажмите "Send"

### Шаг 3: Настройка проекта

#### 3.1 Клонирование репозитория

```bash
git clone https://github.com/yourusername/receipt-bot.git
cd receipt-bot
```

#### 3.2 Установка зависимостей

**Для Linux/Ubuntu:**
```bash
# Установка системных зависимостей
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libzbar0 libgl1-mesa-glx

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
pip install -r requirements.txt
```

**Для Windows:**
```bash
# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка Python зависимостей
pip install -r requirements.txt
```

#### 3.3 Настройка переменных окружения

1. **Скопируйте файл** `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. **Откройте файл** `.env` и заполните переменные:

```env
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Google Sheets Credentials (JSON строка из service-account-key.json)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}

# Google Spreadsheet ID (из URL таблицы)
GOOGLE_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Название листа в таблице (по умолчанию: Receipts)
GOOGLE_WORKSHEET_NAME=Receipts

# Уровень логирования
LOG_LEVEL=INFO
```

**Важно:** Для `GOOGLE_CREDENTIALS_JSON` нужно взять содержимое файла `service-account-key.json` и вставить как одну строку.

### Шаг 4: Тестирование

#### 4.1 Проверка конфигурации

```bash
python test_bot.py
```

Должны увидеть:
```
🧪 Тестирование компонентов бота
==================================================
🔍 Проверка импортов...
✅ QRCodeScanner импортирован
✅ ReceiptParser импортирован
✅ GoogleSheetsManager импортирован

🔍 Тестирование парсера QR-кодов...
✅ Парсинг QR-кода работает
   Извлеченные данные: 8 полей

🔍 Тестирование подключения к Google Sheets...
✅ Подключение к Google Sheets работает

==================================================
📊 Результаты: 3/3 тестов пройдено
✅ Все тесты пройдены успешно!
```

#### 4.2 Запуск бота

```bash
python run.py
```

Должны увидеть:
```
🤖 Запуск Telegram бота для сканирования чеков
==================================================
✅ Все переменные окружения настроены
🚀 Запуск бота...
```

### Шаг 5: Развертывание на сервере

#### 5.1 Подготовка сервера

**Для Ubuntu/Debian:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

#### 5.2 Развертывание с Docker

1. **Скопируйте файлы** на сервер:
   ```bash
   scp -r . user@your-server:/home/user/receipt-bot/
   ```

2. **Подключитесь к серверу:**
   ```bash
   ssh user@your-server
   cd receipt-bot
   ```

3. **Создайте файл** `.env` на сервере с вашими данными

4. **Запустите бота:**
   ```bash
   docker-compose up -d
   ```

5. **Проверьте логи:**
   ```bash
   docker-compose logs -f
   ```

#### 5.3 Развертывание без Docker

1. **Установите зависимости** (см. Шаг 3.2)

2. **Создайте systemd сервис:**
   ```bash
   sudo nano /etc/systemd/system/receipt-bot.service
   ```

   Содержимое файла:
   ```ini
   [Unit]
   Description=Receipt Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/receipt-bot
   Environment=PATH=/home/your-username/receipt-bot/venv/bin
   ExecStart=/home/your-username/receipt-bot/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Запустите сервис:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable receipt-bot
   sudo systemctl start receipt-bot
   sudo systemctl status receipt-bot
   ```

### Шаг 6: Настройка GitHub Actions (опционально)

1. **Создайте репозиторий** на GitHub
2. **Загрузите код** в репозиторий
3. **Добавьте секреты** в настройках репозитория:
   - `TELEGRAM_BOT_TOKEN`
   - `GOOGLE_CREDENTIALS_JSON`
   - `GOOGLE_SPREADSHEET_ID`
4. **Настройте автоматическое развертывание** (файл `.github/workflows/deploy.yml` уже готов)

## 🔧 Настройка и использование

### Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/my_receipts` - Показать мои чеки
- `/stats` - Статистика по чекам

### Как использовать

1. **Найдите бота** в Telegram по username
2. **Нажмите** `/start`
3. **Нажмите** "Сканировать QR-код"
4. **Сфотографируйте** QR-код с чека
5. **Дождитесь** обработки

### Структура данных в Google Sheets

| Колонка | Описание |
|---------|----------|
| ID пользователя | Telegram ID пользователя |
| Дата сканирования | Когда был отсканирован чек |
| Дата чека | Дата из QR-кода чека |
| Время чека | Время из QR-кода чека |
| Сумма чека | Сумма из QR-кода чека |
| ФН чека | Фискальный номер |
| ФД чека | Фискальный документ |
| ФП чека | Фискальный признак |
| ИНН продавца | ИНН продавца |
| Сырой QR код | Исходный QR-код |
| Статус | Статус чека |

## 🐛 Устранение неполадок

### Ошибка "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Ошибка "Google Sheets API not enabled"

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API и Google Drive API

### Ошибка "Permission denied" в Google Sheets

1. Убедитесь, что поделились таблицей с email сервисного аккаунта
2. Проверьте права доступа (должны быть "Editor")

### Бот не отвечает

1. Проверьте токен бота
2. Проверьте логи: `docker-compose logs` или `journalctl -u receipt-bot`

### QR-код не распознается

1. Убедитесь, что QR-код четко виден
2. Попробуйте сфотографировать под другим углом
3. Проверьте, что это QR-код чека (содержит t=, s=, fn=, fd=, fp=)

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи** бота
2. **Запустите тесты** `python test_bot.py`
3. **Проверьте переменные окружения**
4. **Убедитесь, что все API включены**

## 🔄 Обновление

Для обновления бота:

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 📝 Лицензия

Этот проект использует только бесплатные библиотеки, подходящие для коммерческого использования.

---

**Удачи с развертыванием! 🚀**