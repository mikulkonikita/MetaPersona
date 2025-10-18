import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class QRCodeScanner:
    """Класс для сканирования QR-кодов с изображений"""
    
    def __init__(self):
        self.min_qr_size = 50  # Минимальный размер QR-кода в пикселях
    
    def preprocess_image(self, image):
        """Предварительная обработка изображения для лучшего распознавания"""
        try:
            # Конвертируем в оттенки серого
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Применяем размытие для уменьшения шума
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Применяем адаптивную пороговую обработку
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Морфологические операции для очистки
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Ошибка предварительной обработки изображения: {e}")
            return image
    
    def find_qr_codes(self, image):
        """Поиск QR-кодов на изображении"""
        try:
            # Предварительная обработка
            processed = self.preprocess_image(image)
            
            # Поиск QR-кодов
            qr_codes = pyzbar.decode(processed)
            
            # Если не найдено, пробуем с оригинальным изображением
            if not qr_codes:
                qr_codes = pyzbar.decode(image)
            
            # Фильтруем по размеру
            valid_qr_codes = []
            for qr in qr_codes:
                # Получаем координаты и размеры
                rect = qr.rect
                if rect.width >= self.min_qr_size and rect.height >= self.min_qr_size:
                    valid_qr_codes.append(qr)
            
            return valid_qr_codes
            
        except Exception as e:
            logger.error(f"Ошибка поиска QR-кодов: {e}")
            return []
    
    def scan_from_bytes(self, image_bytes):
        """Сканирование QR-кода из байтов изображения"""
        try:
            # Конвертируем байты в изображение
            image = Image.open(io.BytesIO(image_bytes))
            
            # Конвертируем в OpenCV формат
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Ищем QR-коды
            qr_codes = self.find_qr_codes(opencv_image)
            
            if qr_codes:
                # Возвращаем текст первого найденного QR-кода
                return qr_codes[0].data.decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка сканирования QR-кода: {e}")
            return None
    
    def scan_from_pil_image(self, pil_image):
        """Сканирование QR-кода из PIL изображения"""
        try:
            # Конвертируем в OpenCV формат
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Ищем QR-коды
            qr_codes = self.find_qr_codes(opencv_image)
            
            if qr_codes:
                # Возвращаем текст первого найденного QR-кода
                return qr_codes[0].data.decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка сканирования QR-кода: {e}")
            return None
    
    def scan_multiple_qr_codes(self, image_bytes):
        """Сканирование нескольких QR-кодов с одного изображения"""
        try:
            # Конвертируем байты в изображение
            image = Image.open(io.BytesIO(image_bytes))
            
            # Конвертируем в OpenCV формат
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Ищем QR-коды
            qr_codes = self.find_qr_codes(opencv_image)
            
            # Возвращаем список всех найденных QR-кодов
            return [qr.data.decode('utf-8') for qr in qr_codes]
            
        except Exception as e:
            logger.error(f"Ошибка сканирования нескольких QR-кодов: {e}")
            return []