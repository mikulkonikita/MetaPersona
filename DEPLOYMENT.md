# 🚀 Инструкция по развертыванию Telegram бота для сканирования чеков

## 📋 Описание проекта

Telegram бот для сканирования QR-кодов чеков с извлечением и сохранением данных:
- Дата и время чека
- Сумма чека
- ФН, ФД, ФП номера
- ИНН продавца
- ID пользователя и дата сканирования

## 🛠️ Требования

### Системные требования
- Python 3.8+
- Linux/Windows/macOS
- Минимум 512MB RAM
- 1GB свободного места на диске

### Зависимости
- python-telegram-bot
- Pillow (PIL)
- pyzbar
- qrcode

## 📦 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd telegram-receipt-scanner
```

### 2. Создание виртуального окружения

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка системных зависимостей

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install libzbar0 libzbar-dev libgl1-mesa-glx libglib2.0-0
```

#### CentOS/RHEL:
```bash
sudo yum install zbar-devel mesa-libGL glib2
```

#### macOS:
```bash
brew install zbar
```

#### Windows:
Скачайте и установите Visual C++ Redistributable для Visual Studio 2015-2022

### 5. Настройка конфигурации

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфигурацию
nano .env
```

Заполните файл `.env`:
```env
BOT_TOKEN=your_bot_token_here
DATABASE_PATH=receipts.db
LOG_LEVEL=INFO
LOG_FILE=bot.log
TEMP_DIR=/tmp
MAX_PHOTO_SIZE=20971520
PHOTO_TIMEOUT=30
```

### 6. Получение токена бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "Receipt Scanner Bot")
4. Введите username бота (например: "receipt_scanner_bot")
5. Скопируйте полученный токен и вставьте в `.env` файл

## 🚀 Запуск

### Способ 1: Автоматический запуск (рекомендуется)

```bash
# Делаем скрипт исполняемым
chmod +x run.sh

# Запускаем бота
./run.sh
```

### Способ 2: Ручной запуск

```bash
# Активируем виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Запускаем бота
python main.py
```

### Способ 3: Запуск в Docker

```bash
# Сборка образа
docker build -t receipt-scanner-bot .

# Запуск контейнера
docker run -d \
  --name receipt-scanner-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  receipt-scanner-bot
```

### Способ 4: Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## 🔧 Настройка для продакшена

### 1. Настройка systemd (Linux)

Создайте файл `/etc/systemd/system/receipt-scanner-bot.service`:

```ini
[Unit]
Description=Telegram Receipt Scanner Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/telegram-receipt-scanner
Environment=PATH=/path/to/telegram-receipt-scanner/venv/bin
ExecStart=/path/to/telegram-receipt-scanner/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable receipt-scanner-bot
sudo systemctl start receipt-scanner-bot
```

### 2. Настройка nginx (опционально)

Для веб-интерфейса администратора:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Настройка мониторинга

Добавьте в cron для автоматической очистки логов:
```bash
# Очистка логов старше 30 дней
0 2 * * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

## 📊 Администрирование

### Просмотр статистики

```bash
python admin.py stats
```

### Просмотр чеков пользователя

```bash
python admin.py user <user_id>
```

### Экспорт данных

```bash
python admin.py export receipts.csv
```

### Очистка старых данных

```bash
python admin.py cleanup 30  # Удалить чеки старше 30 дней
```

## 🔍 Диагностика проблем

### 1. Проверка логов

```bash
tail -f logs/bot.log
```

### 2. Проверка базы данных

```bash
sqlite3 data/receipts.db
.tables
.schema receipts
SELECT COUNT(*) FROM receipts;
```

### 3. Тестирование QR-кода

```bash
python -c "
from qr_parser import ReceiptQRParser
parser = ReceiptQRParser()
result = parser.parse_qr_code('t=20231201T1430&s=150000&fn=1234567890&i=123&fp=456789&n=1')
print(result)
"
```

### 4. Проверка зависимостей

```bash
python -c "
import pyzbar
from PIL import Image
print('Все зависимости установлены корректно')
"
```

## 🛡️ Безопасность

### 1. Настройка файрвола

```bash
# Разрешить только необходимые порты
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (если нужен веб-интерфейс)
sudo ufw enable
```

### 2. Настройка прав доступа

```bash
# Создаем пользователя для бота
sudo useradd -m -s /bin/bash bot
sudo chown -R bot:bot /path/to/telegram-receipt-scanner
sudo chmod 600 .env
```

### 3. Резервное копирование

```bash
# Создаем скрипт бэкапа
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "backup_$DATE.tar.gz" data/ logs/ .env
EOF

chmod +x backup.sh

# Добавляем в cron
echo "0 3 * * * /path/to/backup.sh" | crontab -
```

## 📈 Масштабирование

### 1. Горизонтальное масштабирование

Для обработки большого количества запросов используйте:
- Load balancer (nginx)
- Несколько экземпляров бота
- Redis для кеширования
- PostgreSQL вместо SQLite

### 2. Вертикальное масштабирование

Увеличьте ресурсы сервера:
- CPU: 2+ ядра
- RAM: 2+ GB
- Диск: SSD 10+ GB

## 🔄 Обновление

```bash
# Остановка бота
sudo systemctl stop receipt-scanner-bot

# Обновление кода
git pull origin main

# Установка новых зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск бота
sudo systemctl start receipt-scanner-bot
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `tail -f logs/bot.log`
2. Проверьте статус: `sudo systemctl status receipt-scanner-bot`
3. Перезапустите бота: `sudo systemctl restart receipt-scanner-bot`
4. Проверьте конфигурацию: `python -c "from config import Config; Config.validate()"`

## 📝 Дополнительные настройки

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| BOT_TOKEN | Токен Telegram бота | Обязательно |
| DATABASE_PATH | Путь к базе данных | receipts.db |
| LOG_LEVEL | Уровень логирования | INFO |
| LOG_FILE | Файл логов | bot.log |
| TEMP_DIR | Временная директория | /tmp |
| MAX_PHOTO_SIZE | Макс. размер фото | 20971520 |
| PHOTO_TIMEOUT | Таймаут обработки | 30 |

### Команды бота

- `/start` - Начать работу
- `/help` - Справка
- `/stats` - Статистика пользователя

### Форматы QR-кодов

Бот поддерживает стандартные форматы QR-кодов чеков:
- `t=YYYYMMDDThhmm&s=сумма&fn=ФН&i=ФД&fp=ФП&n=тип`
- С дополнительными параметрами (ИНН, название организации)