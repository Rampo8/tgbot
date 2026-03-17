# handlers/video.py
from aiogram import types, Router
from utils.downloader import download_video
from config import MAX_FILE_SIZE
import os

router = Router()

@router.message(lambda msg: msg.text and any(x in msg.text for x in ['youtube.com', 'youtu.be', 'rutube.ru', 'instagram.com']))
async def handle_video_link(message: types.Message):
    url = message.text
    wait_msg = await message.answer("⏳ Скачиваю видео...")
    
    try:
        file_path, title = download_video(url)
        
        # Проверка размера
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (>50MB). Попробуйте ссылку на видео меньшего качества.")
            await wait_msg.delete()
            return
        
        await message.answer_document(
            document=types.FSInputFile(file_path),
            caption=f"🎬 {title[:50]}..."
        )
        
        # Удаляем файл после отправки
        os.remove(file_path)
        await wait_msg.delete()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await wait_msg.delete()