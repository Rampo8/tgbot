from PIL import Image
import os
import logging
from config import DOWNLOAD_DIR, PHOTO_SAVE_QUALITY

logger = logging.getLogger(__name__)

PIXEL_SCALE = 8
MAX_TELEGRAM_DIMENSION = 5000  # Максимальный размер по стороне
MAX_TELEGRAM_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

def enhance_photo(image_path):
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size
        
        logger.info(f"Исходный размер: {original_width}x{original_height}")

        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Рассчитываем новый размер
        new_width = original_width * PIXEL_SCALE
        new_height = original_height * PIXEL_SCALE
        
        logger.info(f"После увеличения: {new_width}x{new_height}")
        
        # Ограничение по размеру стороны
        if new_width > MAX_TELEGRAM_DIMENSION or new_height > MAX_TELEGRAM_DIMENSION:
            scale = min(MAX_TELEGRAM_DIMENSION / original_width, MAX_TELEGRAM_DIMENSION / original_height)
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            logger.info(f"Ограничено до: {new_width}x{new_height}")
        
        new_size = (new_width, new_height)
        img_scaled = img.resize(new_size, Image.NEAREST)

        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        new_filename = f"enhanced_{name}.jpg"
        new_path = os.path.join(DOWNLOAD_DIR, new_filename)

        img_scaled.save(new_path, 'JPEG', quality=PHOTO_SAVE_QUALITY, optimize=True)
        
        file_size = os.path.getsize(new_path)
        logger.info(f"Размер файла: {file_size // 1024} КБ")

        return new_path

    except FileNotFoundError:
        raise Exception(f"Файл не найден: {image_path}")
    except Exception as e:
        logger.error(f"Ошибка в enhance_photo: {e}")
        raise Exception(f"Ошибка обработки фото: {str(e)}")


def remove_background(image_path):
    """
    Удаляет фон с изображения.
    Автоматически определяет: людей, животных, предметы.
    
    Args:
        image_path: Путь к исходному изображению
        
    Returns:
        str: Путь к изображению с удалённым фоном
    """
    try:
        from rembg import remove, new_session
        
        img = Image.open(image_path)
        logger.info(f"Обработка изображения: {image_path}, режим: {img.mode}")
        
        # Конвертируем в RGB/RGBA если нужно
        if img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode == 'L':
            img = img.convert('LA')
        
        # Создаём сессию с моделью u2net (универсальная для всех объектов)
        # Другие модели: u2netp (быстрее), u2net_human_seg (только люди), u2net_cloth_seg (одежда)
        session = new_session('u2net')
        
        # Удаляем фон
        img_no_bg = remove(
            img,
            session=session,
            alpha_matting=True,      # Сглаживание краёв
            alpha_matting_foreground_threshold=240,  # Порог переднего плана
            alpha_matting_background_threshold=10,   # Порог фона
            alpha_matting_erode_size=10              # Размер эрозии для чистых краёв
        )
        
        # Сохраняем результат
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        new_filename = f"no_bg_{name}.png"
        new_path = os.path.join(DOWNLOAD_DIR, new_filename)
        
        # Сохраняем в PNG с прозрачностью
        img_no_bg.save(new_path, 'PNG')
        
        logger.info(f"Фон удалён успешно: {new_path}")
        
        return new_path
        
    except ImportError as e:
        logger.error(f"rembg не установлена: {e}")
        raise Exception("Библиотека rembg не установлена. Запустите: pip install rembg")
    except FileNotFoundError:
        logger.error(f"Файл не найден: {image_path}")
        raise Exception(f"Файл не найден: {image_path}")
    except Exception as e:
        logger.error(f"Ошибка в remove_background: {type(e).__name__}: {e}")
        raise Exception(f"Ошибка удаления фона: {str(e)}")