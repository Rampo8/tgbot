import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN, LOG_LEVEL
from handlers import video, photo, start

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
def create_bot_and_dispatcher():
    """
    Создаёт и настраивает бота с увеличенными таймаутами.
    """
    # Настраиваем сессию с большим таймаутом (300 секунд)
    # Убираем неподдерживаемые параметры conn_timeout и другие
    session = AiohttpSession(timeout=300)
    
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(video.router)
    dp.include_router(photo.router)
    
    return bot, dp

# ==================== ОБРАБОТЧИКИ ====================
async def register_additional_handlers(dp):
    """
    Регистрирует дополнительные обработчики.
    """
    
    @dp.message(Command("ping"))
    async def ping_cmd(message: Message):
        """Проверка работоспособности бота"""
        await message.answer("🟢 *Бот работает!*\n\n"
                            f"⏱ Время ответа: минимальное",
                            parse_mode="Markdown")
    
    @dp.message(lambda msg: msg.text and not msg.text.startswith('/'))
    async def handle_unknown_text(message: Message):
        """
        Обработчик неизвестных текстовых сообщений.
        """
        text = message.text.lower()
        
        from handlers.video import is_video_link
        if is_video_link(text):
            await message.answer(
                "🔗 *Я вижу ссылку!*\n\n"
                "Попробуйте отправить её ещё раз.",
                parse_mode="Markdown"
            )
            return
        
        await message.answer(
            "🤔 *Я не понял эту команду.*\n\n"
            "📌 *Что я умею:*\n"
            "• Скачивать видео с YouTube, Rutube, Instagram\n"
            "• Улучшать качество фотографий\n\n"
            "💡 *Отправьте:*\n"
            "• Ссылку на видео\n"
            "• Или фотографию для улучшения\n\n"
            "📚 *Команды:*\n"
            "/start - Главное меню\n"
            "/help - Справка\n"
            "/settings - Настройки",
            parse_mode="Markdown"
        )

# ==================== ЗАПУСК ====================
async def main():
    """
    Основная функция запуска бота.
    """
    logger.info("🚀 Запуск бота...")
    
    # Создаём бота и диспетчер
    bot, dp = create_bot_and_dispatcher()
    
    # Регистрируем дополнительные обработчики
    await register_additional_handlers(dp)
    
    # Проверяем токен
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот авторизован: @{bot_info.username} ({bot_info.first_name})")
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации: {e}")
        logger.error("💡 Проверьте подключение к интернету и доступность Telegram")
        await bot.close()
        return
    
    # Запускаем опрос (polling)
    try:
        logger.info("📡 Бот запущен и ожидает сообщения...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹ Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.close()
        logger.info("👋 Бот остановлен")

# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹ Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")