from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)

# ============================================================
# 🔧 НАСТРОЙКИ - ИЗМЕНИТЕ ЭТИ ЗНАЧЕНИЯ
# ============================================================

# ССЫЛКА НА КАНАЛ - вставьте вашу ссылку ниже
# Примеры:
#   - "https://t.me/durov"
#   - "https://t.me/+AbCdEfGhIjKlMnOp"
#   - "t.me/my_channel"
CHANNEL_LINK = "https://t.me/Rampogames"  # ← ВСТАВЬТЕ ССЫЛКУ НА КАНАЛ ЗДЕСЬ

# ID или username канала (нужен для проверки подписки)
# Если канал публичный - можно указать username без ссылки
# Если приватный - нужен ID канала (начинается с -100)
REQUIRED_CHANNEL = "@Rampogames"  # ← ЗАМЕНИТЕ НА СВОЙ КАНАЛ

# Текст сообщения с просьбой подписаться
# Можно использовать Markdown разметку
SUBSCRIBE_MESSAGE = """
❗️ *Для использования бота необходимо подписаться на наш канал!*

👉 Нажмите кнопку ниже, чтобы перейти в канал
"""

# Текст кнопки для перехода в канал
# {channel} будет заменён на название канала
SUBSCRIBE_BUTTON_TEXT = "📢 Подписаться на {channel}"

# Текст кнопки для проверки подписки
CHECK_SUBSCRIPTION_BUTTON_TEXT = "✅ Я подписался"

# ============================================================
# 📋 ФУНКЦИИ - НЕ МЕНЯЙТЕ КОД НИЖЕ (если не уверены)
# ============================================================

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Проверяет, подписан ли пользователь на обязательный канал.
    
    Args:
        bot: Экземпляр бота
        user_id: ID пользователя для проверки
        
    Returns:
        bool: True если подписан, False если нет
    """
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        
        # Статусы, которые считаются как подписка
        allowed_statuses = ["member", "administrator", "creator"]
        
        is_subscribed = member.status in allowed_statuses
        
        if not is_subscribed:
            logger.info(f"Пользователь {user_id} не подписан на канал {REQUIRED_CHANNEL}")
        else:
            logger.info(f"Пользователь {user_id} подписан на канал {REQUIRED_CHANNEL}")
        
        return is_subscribed
        
    except TelegramBadRequest as e:
        # Ошибки Telegram API
        error_message = str(e).lower()
        
        if "user not found" in error_message:
            logger.error(f"Пользователь {user_id} не найден (возможно, заблокировал бота)")
        elif "chat not found" in error_message or "private channel" in error_message:
            logger.error(f"Канал {REQUIRED_CHANNEL} не найден или бот не администратор")
        elif "bot is not a channel admin" in error_message:
            logger.error(f"Бот не является администратором канала {REQUIRED_CHANNEL}")
        else:
            logger.error(f"Ошибка проверки подписки: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке подписки: {type(e).__name__}: {e}")
        return False


async def get_subscribe_keyboard(bot: Bot):
    """
    Создаёт клавиатуру с кнопкой для подписки.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Получаем название канала для кнопки
    try:
        chat = await bot.get_chat(REQUIRED_CHANNEL)
        channel_name = chat.title if chat.title else REQUIRED_CHANNEL
    except:
        channel_name = REQUIRED_CHANNEL
    
    # Формируем текст кнопки
    button_text = SUBSCRIBE_BUTTON_TEXT.format(channel=channel_name)
    
    # Используем CHANNEL_LINK для кнопки
    invite_link = CHANNEL_LINK
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    url=invite_link
                )
            ],
            [
                InlineKeyboardButton(
                    text=CHECK_SUBSCRIPTION_BUTTON_TEXT,
                    callback_data="check_subscription"
                )
            ]
        ]
    )
    
    return keyboard


async def force_subscribe(bot: Bot, user_id: int):
    """
    Принудительная подписка - проверяет и требует подписку.
    Используется в хендлерах перед основной логикой.
    
    Args:
        bot: Экземпляр бота
        user_id: ID пользователя
        
    Returns:
        tuple: (is_subscribed: bool, message_to_send: str|None, keyboard: InlineKeyboardMarkup|None)
    """
    is_subscribed = await check_subscription(bot, user_id)
    
    if not is_subscribed:
        keyboard = await get_subscribe_keyboard(bot)
        return False, SUBSCRIBE_MESSAGE, keyboard
    
    return True, None, None
