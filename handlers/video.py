
from aiogram import types, Router
from utils.downloader import download_video
from config import MAX_FILE_SIZE, DOWNLOAD_DIR
import os

router = Router()

def is_video_link(text):
   
    domains = ['youtube.com', 'youtu.be', 'rutube.ru', 'instagram.com', 'vimeo.com']
    return any(d in text.lower() for d in domains)

@router.message(lambda msg: msg.text and is_video_link(msg.text))
async def handle_video(message: types.Message):
    url = message.text
    wait = await message.answer("⏳ Скачиваю видео...")
    
    try:
        # Скачиваем видео
        file_path, title = download_video(url)
        
        # Проверяем размер
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            await message.answer("❌ Файл больше 50 МБ. Попробуйте короткое видео.")
            await wait.delete()
            return
        
        # Отправляем видео
        await message.answer_document(
            document=types.FSInputFile(file_path),
            caption=f"🎬 {title[:50]}"
        )
        
        # Удаляем файл
        os.remove(file_path)
        await wait.delete()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:200]}")
        await wait.delete()