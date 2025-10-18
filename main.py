#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot для сканирования QR-кодов чеков
"""

import logging
import os
from typing import Optional, Dict, Any

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import Config
from database import ReceiptDatabase
from qr_parser import ReceiptQRParser

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Инициализация компонентов
Config.validate()
db = ReceiptDatabase(Config.DATABASE_PATH)
qr_parser = ReceiptQRParser()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_text = f"""
Привет, {user.first_name}! 👋

Я бот для сканирования QR-кодов чеков. 

📱 **Как использовать:**
1. Отправь мне фото с QR-кодом чека
2. Я извлеку данные и сохраню их
3. Получишь подтверждение о принятии чека

🔍 **Что я извлекаю из чека:**
• Дата и время чека
• Сумма чека
• ФН, ФД, ФП номера
• ИНН продавца

Просто отправь фото с QR-кодом! 📸
    """
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🤖 **Помощь по боту**

**Команды:**
/start - Начать работу с ботом
/help - Показать эту справку
/stats - Показать статистику ваших чеков

**Как сканировать чек:**
1. Сделайте четкое фото QR-кода на чеке
2. Отправьте фото боту
3. Дождитесь обработки

**Требования к фото:**
• QR-код должен быть четко виден
• Хорошее освещение
• QR-код не должен быть поврежден

Если у вас есть вопросы, обратитесь к администратору.
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user_id = update.effective_user.id
    
    try:
        stats = db.get_user_stats(user_id)
        
        if stats and stats['total_receipts'] > 0:
            stats_text = f"""
📊 **Ваша статистика:**

📄 Всего чеков: {stats['total_receipts']}
💰 Общая сумма: {stats['total_amount']:.2f} ₽
📅 Первый чек: {stats['first_scan']}
📅 Последний чек: {stats['last_scan']}
            """
        else:
            stats_text = "📊 У вас пока нет отсканированных чеков."
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await update.message.reply_text("❌ Ошибка получения статистики.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий с QR-кодами"""
    user = update.effective_user
    photo = update.message.photo[-1]  # Берем фото наивысшего качества
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("🔍 Обрабатываю фото...")
    
    try:
        # Скачиваем фото
        file = await context.bot.get_file(photo.file_id)
        file_path = f"temp_photo_{user.id}.jpg"
        await file.download_to_drive(file_path)
        
        # Пытаемся найти и декодировать QR-код
        qr_data = None
        try:
            from pyzbar import pyzbar
            from PIL import Image
            
            # Открываем изображение
            image = Image.open(file_path)
            
            # Ищем QR-коды
            qr_codes = pyzbar.decode(image)
            
            if qr_codes:
                # Берем первый найденный QR-код
                qr_data = qr_codes[0].data.decode('utf-8')
                logger.info(f"Найден QR-код: {qr_data}")
            else:
                await processing_msg.edit_text("❌ QR-код не найден на фото. Попробуйте сделать более четкое фото.")
                return
                
        except ImportError:
            await processing_msg.edit_text("❌ Ошибка: не установлена библиотека для чтения QR-кодов.")
            return
        except Exception as e:
            logger.error(f"Ошибка чтения QR-кода: {e}")
            await processing_msg.edit_text("❌ Ошибка при чтении QR-кода. Попробуйте другое фото.")
            return
        finally:
            # Удаляем временный файл
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Парсим данные чека
        receipt_data = qr_parser.parse_qr_code(qr_data)
        if not receipt_data:
            await processing_msg.edit_text("❌ Не удалось извлечь данные из QR-кода. Убедитесь, что это QR-код чека.")
            return
        
        # Валидируем данные чека
        if not qr_parser.validate_receipt_data(receipt_data):
            await processing_msg.edit_text("❌ В QR-коде отсутствуют необходимые данные. Убедитесь, что это корректный QR-код чека.")
            return
        
        # Сохраняем в базу данных
        success = db.save_receipt(user.id, receipt_data)
        
        if success:
            # Формируем сообщение с данными чека
            receipt_info = f"""
✅ **Чек принят!**

📅 Дата: {receipt_data.get('receipt_date', 'Не указана')}
🕐 Время: {receipt_data.get('receipt_time', 'Не указано')}
💰 Сумма: {receipt_data.get('total_amount', 0):.2f} ₽
🏪 ИНН продавца: {receipt_data.get('seller_inn', 'Не указан')}

📋 **Технические данные:**
• ФН: {receipt_data.get('fn_number', 'Не указан')}
• ФД: {receipt_data.get('fd_number', 'Не указан')}
• ФП: {receipt_data.get('fp_number', 'Не указан')}
            """
            await processing_msg.edit_text(receipt_info, parse_mode=ParseMode.MARKDOWN)
        else:
            await processing_msg.edit_text("⚠️ Ваш чек уже был ранее зарегистрирован, сканируйте другой чек.")
    
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка при обработке фото. Попробуйте еще раз.")

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling()

if __name__ == '__main__':
    main()