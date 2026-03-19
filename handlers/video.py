
from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from utils.downloader import download_video
from utils.video_processor import process_video, cleanup_files
from utils.subscription import check_subscription, get_subscribe_keyboard, SUBSCRIBE_MESSAGE
from config import MAX_FILE_SIZE, DOWNLOAD_DIR
import os
import logging
from handlers.start import UserMode

logger = logging.getLogger(__name__)

router = Router()

def is_video_link(text):
    domains = ['youtube.com', 'youtu.be', 'rutube.ru', 'instagram.com', 'vimeo.com']
    return any(d in text.lower() for d in domains)

def get_back_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(text="↩️ В главное меню", callback_data="back_to_menu")
        ]]
    )

async def check_sub_required(message: types.Message, state: FSMContext) -> bool:
    """Проверяет подписку. Возвращает True если OK, False если нужно подписаться."""
    bot = message.bot
    is_subscribed = await check_subscription(bot, message.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        await state.clear()
        await message.answer(
            text=SUBSCRIBE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return False
    return True

@router.message(F.text, StateFilter(UserMode.video), lambda msg: is_video_link(msg.text))
async def handle_video(message: types.Message, state: FSMContext):
    # Проверка подписки
    if not await check_sub_required(message, state):
        return

    url = message.text
    wait = await message.answer("⏳ Скачиваю видео...")

    try:
        file_path, title = download_video(url)
        logger.info(f"Видео скачано: {file_path}")

        # Обрабатываем видео (сжатие + разбиение)
        await wait.edit_text("🔄 Обрабатываю видео...")
        file_paths, video_title, was_compressed = process_video(file_path, max_height=720)

        logger.info(f"Обработано: {len(file_paths)} файлов, название: {video_title}, сжато: {was_compressed}")
        logger.info(f"Файлы: {file_paths}")

        # Проверяем существование файлов
        for path in file_paths:
            if not os.path.exists(path):
                raise Exception(f"Файл не найден: {path}")

        # Отправляем все части
        for i, path in enumerate(file_paths):
            if len(file_paths) > 1:
                caption = f"🎬 {video_title[:50]}\n\n📦 Часть {i+1}/{len(file_paths)}"
            elif was_compressed:
                caption = f"🎬 {video_title[:50]}\n\n✅ Сжато для отправки"
            else:
                caption = f"🎬 {video_title[:50]}"

            logger.info(f"Отправка файла {i+1}/{len(file_paths)}: {path}")

            await message.answer_document(
                document=types.FSInputFile(path),
                caption=caption,
                reply_markup=get_back_keyboard() if i == len(file_paths) - 1 else None
            )

        # Удаляем временные файлы
        cleanup_files(file_paths)
        await wait.delete()

    except Exception as e:
        logger.error(f"Ошибка в handle_video: {type(e).__name__}: {e}")
        await message.answer(
            f"❌ Ошибка: {str(e)[:200]}",
            reply_markup=get_back_keyboard()
        )
        await wait.delete()