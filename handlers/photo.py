# handlers/photo.py
from aiogram import types, Router
from utils.enhancer import enhance_photo
import os

router = Router()

@router.message(lambda msg: msg.photo)
async def handle_photo(message: types.Message):
    wait_msg = await message.answer("⏳ Улучшаю качество фото...")
    
    try:
        # Скачиваем фото от пользователя
        photo = message.photo[-1]  # Берем лучшее качество
        file = await message.bot.get_file(photo.file_id)
        file_path = os.path.join('downloads', file.file_path)
        await message.bot.download_file(file.file_path, file_path)
        
        # Улучшаем
        enhanced_path = enhance_photo(file_path)
        
        await message.answer_photo(
            photo=types.FSInputFile(enhanced_path),
            caption="✨ Улучшенное фото"
        )
        
        # Удаляем файлы
        os.remove(file_path)
        os.remove(enhanced_path)
        await wait_msg.delete()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await wait_msg.delete()