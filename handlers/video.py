from aiogram import types, Router
from utils.downloader import download_video
from utils.splitter import split_file, get_file_size_human
from config import MAX_FILE_SIZE, DOWNLOAD_DIR
import os
import asyncio

router = Router()

@router.message(lambda msg: msg.text and is_video_link(msg.text))
async def handle_video_link(message: types.Message):
    """
    Обработчик ссылок на видео (YouTube, Rutube, Instagram и др.)
    """
    url = message.text
    
    # Отправляем сообщение о начале обработки
    wait_msg = await message.answer("⏳ *Скачиваю видео...*\n\n"
                                    "Это может занять несколько минут.",
                                    parse_mode="Markdown")
    
    try:
        # Скачиваем видео
        file_path, title = download_video(url)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            raise Exception("Файл не был создан после загрузки")
        
        # Получаем размер файла
        file_size = os.path.getsize(file_path)
        file_size_human = get_file_size_human(file_path)
        
        # Обновляем статус
        await wait_msg.edit_text(
            f"⏳ *Видео готово!*\n\n"
            f"📦 Размер: `{file_size_human}`\n"
            f"🎬 Название: `{title[:50]}...`\n\n"
            "📤 *Отправляю...*",
            parse_mode="Markdown"
        )
        
        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            # Файл больше 50 МБ — разбиваем на части
            await message.answer(
                f"⚠️ *Файл большой ({file_size_human})*\n\n"
                "Отправляю частями. Скачайте все части и объедините их.",
                parse_mode="Markdown"
            )
            
            chunks = split_file(file_path, chunk_size=49 * 1024 * 1024)
            
            for i, chunk in enumerate(chunks):
                chunk_size = get_file_size_human(chunk)
                await message.answer_document(
                    document=types.FSInputFile(chunk),
                    caption=f"🎬 {title[:40]}...\n"
                           f"📦 Часть {i + 1}/{len(chunks)}\n"
                           f"💾 Размер: {chunk_size}",
                    parse_mode="Markdown"
                )
                # Удаляем часть после отправки
                os.remove(chunk)
                # Небольшая пауза чтобы не спамить
                await asyncio.sleep(0.5)
        else:
            # Файл в пределах лимита — отправляем целиком
            await message.answer_document(
                document=types.FSInputFile(file_path),
                caption=f"🎬 {title[:50]}...\n"
                       f"💾 Размер: {file_size_human}",
                parse_mode="Markdown"
            )
        
        # Удаляем исходный файл
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Удаляем сообщение о статусе
        await wait_msg.delete()
        
    except Exception as e:
        error_text = f"❌ *Ошибка:*\n\n`{str(e)[:200]}`\n\n"
        error_text += "💡 *Совет:*\n"
        error_text += "• Проверьте ссылку\n"
        error_text += "• Попробуйте другое видео\n"
        error_text += "• Убедитесь что видео доступно в вашем регионе"
        
        await message.answer(
            text=error_text,
            parse_mode="Markdown"
        )
        
        # Пытаемся удалить сообщение о статусе
        try:
            await wait_msg.delete()
        except:
            pass
        
        # Чистим файлы если они остались
        cleanup_downloads()


def is_video_link(text):
    """
    Проверяет, является ли текст ссылкой на видео.
    """
    video_domains = [
        'youtube.com', 'youtu.be',
        'rutube.ru', 'rutube.com',
        'instagram.com', 'instagr.am',
        'vimeo.com', 'tiktok.com',
        'twitter.com', 'x.com',
        'facebook.com', 'fb.watch'
    ]
    
    text_lower = text.lower()
    return any(domain in text_lower for domain in video_domains)


def cleanup_downloads():
    """
    Очищает старые файлы из папки загрузок.
    """
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Ошибка очистки: {e}")