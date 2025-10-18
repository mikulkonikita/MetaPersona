import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from PIL import Image
import io

# Импортируем наши модули
from qr_scanner import QRCodeScanner
from receipt_parser import ReceiptParser
from google_sheets_manager import GoogleSheetsManager
from config import *

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class ReceiptBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.google_credentials = GOOGLE_CREDENTIALS_JSON
        self.spreadsheet_id = GOOGLE_SPREADSHEET_ID
        self.worksheet_name = GOOGLE_WORKSHEET_NAME
        
        # Инициализация компонентов
        self.qr_scanner = QRCodeScanner()
        self.receipt_parser = ReceiptParser()
        self.sheets_manager = GoogleSheetsManager(
            self.google_credentials, 
            self.spreadsheet_id, 
            self.worksheet_name
        )

# Создаем экземпляр бота
bot = ReceiptBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🔍 *Бот для сканирования чеков*

Привет! Я помогу вам отсканировать QR-код с чека и сохранить информацию о нем.

📱 *Как использовать:*
1. Нажмите кнопку "Сканировать QR-код"
2. Сфотографируйте QR-код с чека
3. Бот автоматически извлечет данные и сохранит их

✅ *Что я извлекаю из чека:*
• Дата и время чека
• Сумма чека
• ФН, ФД, ФП чека
• ИНН продавца

Нажмите кнопку ниже, чтобы начать сканирование!
    """
    
    keyboard = [
        [InlineKeyboardButton("📷 Сканировать QR-код", callback_data="scan_qr")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 *Помощь по использованию бота*

*Команды:*
/start - Начать работу с ботом
/help - Показать эту справку
/my_receipts - Показать мои чеки
/stats - Статистика по чекам

*Как сканировать чек:*
1. Нажмите "Сканировать QR-код"
2. Сфотографируйте QR-код с чека
3. Дождитесь обработки

*Что происходит после сканирования:*
• Бот извлекает данные из QR-кода
• Проверяет, не был ли чек уже отсканирован
• Сохраняет данные в таблицу
• Уведомляет о результате

*Если чек уже был отсканирован:*
Бот сообщит: "Ваш чек уже был ранее зарегистрирован, сканируйте другой чек"

*Если чек принят:*
Бот сообщит: "Чек принят"
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def my_receipts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /my_receipts"""
    try:
        user_id = update.effective_user.id
        receipts = bot.sheets_manager.get_user_receipts(user_id, limit=5)
        
        if not receipts:
            await update.message.reply_text("📄 У вас пока нет сохраненных чеков.")
            return
        
        text = "📄 *Ваши последние чеки:*\n\n"
        
        for i, receipt in enumerate(receipts, 1):
            date = receipt.get('Дата чека', 'Неизвестно')
            time = receipt.get('Время чека', '')
            sum_amount = receipt.get('Сумма чека', 'Неизвестно')
            status = receipt.get('Статус', 'Неизвестно')
            
            text += f"{i}. {date}"
            if time:
                text += f" {time}"
            text += f"\n💰 Сумма: {sum_amount} руб.\n📊 Статус: {status}\n\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Ошибка получения чеков пользователя: {e}")
        await update.message.reply_text("❌ Ошибка при получении ваших чеков.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    try:
        stats = bot.sheets_manager.get_receipt_statistics()
        
        if not stats:
            await update.message.reply_text("📊 Статистика недоступна.")
            return
        
        text = "📊 *Статистика по чекам:*\n\n"
        text += f"📄 Всего чеков: {stats.get('total_receipts', 0)}\n"
        text += f"👥 Уникальных пользователей: {stats.get('unique_users', 0)}\n\n"
        
        status_counts = stats.get('status_counts', {})
        if status_counts:
            text += "*По статусам:*\n"
            for status, count in status_counts.items():
                text += f"• {status}: {count}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "scan_qr":
        await query.edit_message_text(
            "📷 *Сканирование QR-кода*\n\nОтправьте мне фотографию QR-кода с чека.\n\n*Советы для лучшего сканирования:*\n• Убедитесь, что QR-код четко виден\n• Избегайте бликов и теней\n• QR-код должен быть полностью в кадре",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "help":
        help_text = """
📖 *Помощь по использованию бота*

*Как сканировать чек:*
1. Отправьте фотографию QR-кода с чека
2. Дождитесь обработки

*Что происходит после сканирования:*
• Бот извлекает данные из QR-кода
• Проверяет, не был ли чек уже отсканирован
• Сохраняет данные в таблицу
• Уведомляет о результате

*Если чек уже был отсканирован:*
Бот сообщит: "Ваш чек уже был ранее зарегистрирован, сканируйте другой чек"

*Если чек принят:*
Бот сообщит: "Чек принят"
        """
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif query.data == "back_to_start":
        welcome_text = """
🔍 *Бот для сканирования чеков*

Привет! Я помогу вам отсканировать QR-код с чека и сохранить информацию о нем.

📱 *Как использовать:*
1. Нажмите кнопку "Сканировать QR-код"
2. Сфотографируйте QR-код с чека
3. Бот автоматически извлечет данные и сохранит их

✅ *Что я извлекаю из чека:*
• Дата и время чека
• Сумма чека
• ФН, ФД, ФП чека
• ИНН продавца

Нажмите кнопку ниже, чтобы начать сканирование!
        """
        keyboard = [
            [InlineKeyboardButton("📷 Сканировать QR-код", callback_data="scan_qr")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий с QR-кодами"""
    try:
        # Получаем информацию о фото
        photo = update.message.photo[-1]  # Берем фото наивысшего качества
        file = await context.bot.get_file(photo.file_id)
        
        # Скачиваем фото
        photo_data = await file.download_as_bytearray()
        
        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text("🔄 Обрабатываю QR-код...")
        
        # Сканируем QR-код с изображения
        qr_text = bot.qr_scanner.scan_from_bytes(photo_data)
        
        if not qr_text:
            await processing_msg.edit_text("❌ QR-код не найден на изображении. Убедитесь, что QR-код четко виден и полностью в кадре.")
            return
        
        # Парсим данные из QR-кода
        receipt_data = bot.receipt_parser.parse_receipt_qr(qr_text)
        
        if not receipt_data:
            await processing_msg.edit_text("❌ Не удалось извлечь данные из QR-кода. Попробуйте сфотографировать QR-код более четко.")
            return
        
        # Проверяем валидность данных чека
        if not bot.receipt_parser.is_valid_receipt(receipt_data):
            validation_errors = receipt_data.get('validation_errors', [])
            error_text = "❌ Данные чека некорректны:\n" + "\n".join(validation_errors)
            await processing_msg.edit_text(error_text)
            return
        
        # Проверяем на дубликат
        if bot.sheets_manager.check_duplicate_receipt(receipt_data['fn'], receipt_data['fd'], receipt_data['fp']):
            await processing_msg.edit_text("⚠️ Ваш чек уже был ранее зарегистрирован, сканируйте другой чек")
            return
        
        # Сохраняем в Google Sheets
        if bot.sheets_manager.save_receipt(update.effective_user.id, qr_text, receipt_data):
            # Показываем краткую сводку по чеку
            summary = bot.receipt_parser.get_receipt_summary(receipt_data)
            success_text = f"✅ Чек принят\n\n{summary}"
            await processing_msg.edit_text(success_text)
        else:
            await processing_msg.edit_text("❌ Ошибка при сохранении чека. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    # Проверяем, является ли текст QR-кодом чека
    if any(keyword in text.lower() for keyword in ['t=', 's=', 'fn=', 'fd=', 'fp=']):
        # Обрабатываем как QR-код в текстовом виде
        processing_msg = await update.message.reply_text("🔄 Обрабатываю QR-код...")
        
        # Парсим данные из QR-кода
        receipt_data = bot.receipt_parser.parse_receipt_qr(text)
        
        if not receipt_data:
            await processing_msg.edit_text("❌ Не удалось извлечь данные из QR-кода.")
            return
        
        # Проверяем валидность данных чека
        if not bot.receipt_parser.is_valid_receipt(receipt_data):
            validation_errors = receipt_data.get('validation_errors', [])
            error_text = "❌ Данные чека некорректны:\n" + "\n".join(validation_errors)
            await processing_msg.edit_text(error_text)
            return
        
        # Проверяем на дубликат
        if bot.sheets_manager.check_duplicate_receipt(receipt_data['fn'], receipt_data['fd'], receipt_data['fp']):
            await processing_msg.edit_text("⚠️ Ваш чек уже был ранее зарегистрирован, сканируйте другой чек")
            return
        
        # Сохраняем в Google Sheets
        if bot.sheets_manager.save_receipt(update.effective_user.id, text, receipt_data):
            # Показываем краткую сводку по чеку
            summary = bot.receipt_parser.get_receipt_summary(receipt_data)
            success_text = f"✅ Чек принят\n\n{summary}"
            await processing_msg.edit_text(success_text)
        else:
            await processing_msg.edit_text("❌ Ошибка при сохранении чека. Попробуйте позже.")
    else:
        # Обычное текстовое сообщение
        await update.message.reply_text(
            "📷 Отправьте мне фотографию QR-кода с чека или нажмите /start для начала работы."
        )

def main():
    """Основная функция запуска бота"""
    if not bot.bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен")
        return
    
    # Создаем приложение
    application = Application.builder().token(bot.bot_token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("my_receipts", my_receipts_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()