from PIL import Image, ImageEnhance
import os
from config import DOWNLOAD_DIR, PHOTO_ENHANCE_SHARPNESS, PHOTO_ENHANCE_CONTRAST, PHOTO_ENHANCE_BRIGHTNESS, PHOTO_SAVE_QUALITY

def enhance_photo(image_path):
    try:
        img = Image.open(image_path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(PHOTO_ENHANCE_SHARPNESS)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(PHOTO_ENHANCE_CONTRAST)
        
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(PHOTO_ENHANCE_BRIGHTNESS)
        
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        new_filename = f"enhanced_{name}.jpg"
        new_path = os.path.join(DOWNLOAD_DIR, new_filename)
        
        img.save(new_path, 'JPEG', quality=PHOTO_SAVE_QUALITY, optimize=True)
        
        return new_path
        
    except FileNotFoundError:
        raise Exception(f"Файл не найден: {image_path}")
    except Exception as e:
        raise Exception(f"Ошибка обработки фото: {str(e)}")