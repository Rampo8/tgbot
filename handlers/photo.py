from aiogram import types, Router
from utils.enhancer import enhance_photo
from config import DOWNLOAD_DIR
import os
import asyncio

router = Router()

@router.message(lambda msg: msg.photo)
async def handle_photo(message: types.Message):
    wait_msg = await message.answer("⏳ *Улучшаю качество фото...*\n\n"
                                    "Применяю: резкость, контраст, яркость",
                                    parse_mode="Markdown")
    
    try:
        photo = message.photo[-1]
        
        file = await message.bot.get_file(photo.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, file.file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        await message.bot.download_file(file.file_path, file_path)
        
        original_size = os.path.getsize(file_path)
        
        await wait_msg.edit_text("⏳ *Обрабатываю...*")
        
        enhanced_path = enhance_photo(file_path)
        
        enhanced_size = os.path.getsize(enhanced_path)
        
        await wait_msg.edit_text("✅ *Готово! Отправляю...*")
        
        await message.answer_photo(
            photo=types.FSInputFile(enhanced_path),
            caption=(
                "✨ *Фото улучшено!*\n\n"
                f"📦 Исходный размер: `{original_size // 1024} КБ`\n"
                f"📦 Новый размер: `{enhanced_size // 1024} КБ`\n\n"
                "🔧 *Применено:*\n"
                "• Повышена резкость\n"
                "• Увеличен контраст\n"
                "• Коррекция яркости"
            ),
            parse_mode="Markdown"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(enhanced_path):
            os.remove(enhanced_path)
        
        await wait_msg.delete()
        
    except FileNotFoundError as e:
        await message.answer(
            "❌ *Ошибка: Файл не найден*\n\n"
            "Попробуйте отправить фото ещё раз.",
            parse_mode="Markdown"
        )
        try:
            await wait_msg.delete()
        except:
            pass
        
    except Exception as e:
        error_text = (
            "❌ *Ошибка обработки фото*\n\n"
            f"`{str(e)[:200]}`\n\n"
            "💡 *Возможные причины:*\n"
            "• Повреждённый файл\n"
            "• Неподдерживаемый формат\n"
            "• Недостаточно памяти"
        )
        
        await message.answer(
            text=error_text,
            parse_mode="Markdown"
        )
        
        try:
            await wait_msg.delete()
        except:
            pass
        
        cleanup_photo_files()


@router.message(lambda msg: msg.document and is_image_document(msg.document))
async def handle_image_document(message: types.Message):
    """
    Обработчик изображений отправленных как документ (без сжатия)
    """
    wait_msg = await message.answer("⏳ *Улучшаю качество фото...*\n\n"
                                    "Обработка файла без сжатия",
                                    parse_mode="Markdown")
    
    try:
        file = await message.bot.get_file(message.document.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, file.file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await message.bot.download_file(file.file_path, file_path)
        
        enhanced_path = enhance_photo(file_path)
        
        await message.answer_document(
            document=types.FSInputFile(enhanced_path),
            caption="✨ *Фото улучшено!* (отправлено как документ)",
            parse_mode="Markdown"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(enhanced_path):
            os.remove(enhanced_path)
        await wait_msg.delete()
    except Exception as e:
        await message.answer(
            f"❌ *Ошибка:* `{str(e)[:200]}`",
            parse_mode="Markdown"
        )
        try:
            await wait_msg.delete()
        except:
            pass
def is_image_document(document):
    image_mime_types = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
        'image/bmp'
    ]
    return document.mime_type in image_mime_types


def cleanup_photo_files():
   
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            if filename.startswith('enhanced_') or filename.endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Ошибка очистки фото: {e}")