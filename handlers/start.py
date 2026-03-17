from aiogram import types, Router
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    """
    Обработчик команды /start
    Показывает пользователю информацию о возможностях бота
    """
    welcome_text = (
        "👋 *Привет! Я медиа-бот для работы с файлами.*\n\n"
        "🎬 *Скачать видео:*\n"
        "Отправь ссылку на YouTube, Rutube, Instagram или другой сайт\n\n"
        "📸 *Улучшить фото:*\n"
        "Отправь фото, и я улучшу его качество (резкость, контраст, яркость)\n\n"
        "⚠️ *Ограничения:*\n"
        "• Максимальный размер файла: 50 МБ\n"
        "• Большие видео будут разбиты на части\n\n"
        "🚀 *Начинай! Отправь ссылку или фото.*"
    )
    
    await message.answer(
        text=welcome_text,
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def help_cmd(message: types.Message):
    """
    Обработчик команды /help
    Показывает подробную справку
    """
    help_text = (
        "📚 *Справка по боту*\n\n"
        "🔹 *Команды:*\n"
        "/start - Запустить бота\n"
        "/help - Показать эту справку\n\n"
        "🔹 *Поддерживаемые сайты:*\n"
        "• YouTube (youtube.com, youtu.be)\n"
        "• Rutube (rutube.ru)\n"
        "• Instagram (instagram.com)\n"
        "• И ещё 1000+ сайтов через yt-dlp\n\n"
        "🔹 *Форматы:*\n"
        "• Видео: MP4 (до 480p)\n"
        "• Фото: JPEG (улучшенное качество)\n\n"
        "🔹 *Лимиты:*\n"
        "• Файлы до 50 МБ (стандарт Telegram)\n"
        "• Большие файлы разбиваются на части\n\n"
        "💡 *Совет:*\n"
        "Для лучшего качества видео отправляйте короткие ролики"
    )
    
    await message.answer(
        text=help_text,
        parse_mode="Markdown"
    )


@router.message(Command("settings"))
async def settings_cmd(message: types.Message):
    """
    Обработчик команды /settings
    Показывает текущие настройки бота
    """
    from config import (
        MAX_FILE_SIZE, 
        VIDEO_MAX_HEIGHT, 
        PHOTO_ENHANCE_SHARPNESS,
        PHOTO_ENHANCE_CONTRAST,
        PHOTO_ENHANCE_BRIGHTNESS
    )
    
    settings_text = (
        "⚙️ *Текущие настройки:*\n\n"
        f"📦 Макс. размер файла: `{MAX_FILE_SIZE // 1024 // 1024} МБ`\n"
        f"🎬 Качество видео: `{VIDEO_MAX_HEIGHT}p`\n"
        f"📸 Резкость фото: `{PHOTO_ENHANCE_SHARPNESS}x`\n"
        f"📸 Контраст фото: `{PHOTO_ENHANCE_CONTRAST}x`\n"
        f"📸 Яркость фото: `{PHOTO_ENHANCE_BRIGHTNESS}x`"
    )
    
    await message.answer(
        text=settings_text,
        parse_mode="Markdown"
    )