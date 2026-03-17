# utils/enhancer.py
from PIL import Image, ImageEnhance
import os
from config import DOWNLOAD_DIR

def enhance_photo(image_path):
    """Улучшает качество фото (резкость, контраст, яркость)"""
    try:
        img = Image.open(image_path)
        
        # Увеличиваем резкость
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        # Увеличиваем контраст
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Увеличиваем яркость
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        
        # Сохраняем
        base_name = os.path.basename(image_path)
        new_path = os.path.join(DOWNLOAD_DIR, f"enhanced_{base_name}")
        img.save(new_path, quality=95)
        
        return new_path
    except Exception as e:
        raise Exception(f"Ошибка обработки фото: {str(e)}")