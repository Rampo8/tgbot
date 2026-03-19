from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.subscription import check_subscription, get_subscribe_keyboard, SUBSCRIBE_MESSAGE

router = Router()

class UserMode(StatesGroup):
    video = State()
    photo = State()
    bg_remove = State()

@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext, bot: types.Bot):
    await state.clear()
    
    # Проверка подписки
    is_subscribed = await check_subscription(bot, message.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        await message.answer(
            text=SUBSCRIBE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    # Если подписан - показываем главное меню
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Скачать видео с YouTube", callback_data="mode_video"),
            ],
            [
                InlineKeyboardButton(text="📸 Улучшить фото", callback_data="mode_photo"),
            ],
            [
                InlineKeyboardButton(text="🖼️ Убрать фон с фото", callback_data="mode_bg_remove"),
            ],
        ]
    )
    
    welcome_text = (
        "👋 *Привет! Я медиа-бот.*\n\n"
        "Выберите режим работы:"
    )

    await message.answer(
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "mode_video")
async def set_video_mode(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    # Проверяем подписку ещё раз
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        await callback.answer("❗️ Сначала нужно подписаться на канал!", show_alert=True)
        return
    
    await state.set_state(UserMode.video)
    await callback.message.edit_text(
        "🎬 *Режим: Скачать видео с YouTube*\n\n"
        "Отправьте ссылку на видео:",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "mode_photo")
async def set_photo_mode(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        await callback.answer("❗️ Сначала нужно подписаться на канал!", show_alert=True)
        return
    
    await state.set_state(UserMode.photo)
    await callback.message.edit_text(
        "📸 *Режим: Улучшить фото*\n\n"
        "Отправьте фото для улучшения:",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "mode_bg_remove")
async def set_bg_remove_mode(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        await callback.answer("❗️ Сначала нужно подписаться на канал!", show_alert=True)
        return
    
    await state.set_state(UserMode.bg_remove)
    await callback.message.edit_text(
        "🖼️ *Режим: Убрать фон с фото*\n\n"
        "Отправьте фото для удаления фона:",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "check_subscription")
async def check_sub(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if is_subscribed:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎬 Скачать видео с YouTube", callback_data="mode_video")],
                [InlineKeyboardButton(text="📸 Улучшить фото", callback_data="mode_photo")],
                [InlineKeyboardButton(text="🖼️ Убрать фон с фото", callback_data="mode_bg_remove")],
            ]
        )
        await callback.message.edit_text(
            "✅ *Спасибо за подписку!*\n\n"
            "Выберите режим работы:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        keyboard = await get_subscribe_keyboard(bot)
        await callback.answer("❗️ Вы ещё не подписаны! Нажмите кнопку ниже.", show_alert=False)
        await callback.message.edit_text(
            text=SUBSCRIBE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard
        )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    await state.clear()
    await callback.answer()
    
    # Проверяем подписку
    is_subscribed = await check_subscription(bot, callback.from_user.id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        try:
            await callback.message.edit_text(
                text=SUBSCRIBE_MESSAGE,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except:
            await callback.message.answer(
                text=SUBSCRIBE_MESSAGE,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Скачать видео с YouTube", callback_data="mode_video")],
            [InlineKeyboardButton(text="📸 Улучшить фото", callback_data="mode_photo")],
            [InlineKeyboardButton(text="🖼️ Убрать фон с фото", callback_data="mode_bg_remove")],
        ]
    )
    try:
        await callback.message.edit_text(
            "👋 *Привет! Я медиа-бот.*\n\n"
            "Выберите режим работы:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        # Если не удалось редактировать - отправляем новое сообщение
        await callback.message.answer(
            "👋 *Привет! Я медиа-бот.*\n\n"
            "Выберите режим работы:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )


@router.message(Command("help"))
async def help_cmd(message: types.Message):
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