from PIL import Image, ImageEnhance
import os
from config import DOWNLOAD_DIR, PHOTO_ENHANCE_SHARPNESS, PHOTO_ENHANCE_CONTRAST, PHOTO_ENHANCE_BRIGHTNESS, PHOTO_SAVE_QUALITY

def enhance_photo(image_path):
    """
    Улучшает качество фото: резкость, контраст, яркость.
    Возвращает путь к улучшенному файлу.
    """
    try:
        # Открываем изображение
        img = Image.open(image_path)
        
        # Конвертируем в RGB если нужно (для PNG с прозрачностью)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Увеличиваем резкость
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(PHOTO_ENHANCE_SHARPNESS)
        
        # Увеличиваем контраст
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(PHOTO_ENHANCE_CONTRAST)
        
        # Увеличиваем яркость
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(PHOTO_ENHANCE_BRIGHTNESS)
        
        # Формируем имя выходного файла
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        new_filename = f"enhanced_{name}.jpg"
        new_path = os.path.join(DOWNLOAD_DIR, new_filename)
        
        # Сохраняем с высоким качеством
        img.save(new_path, 'JPEG', quality=PHOTO_SAVE_QUALITY, optimize=True)
        
        return new_path
        
    except FileNotFoundError:
        raise Exception(f"Файл не найден: {image_path}")
    except Exception as e:
        raise Exception(f"Ошибка обработки фото: {str(e)}")