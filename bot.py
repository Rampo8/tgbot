import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN, LOG_LEVEL
from handlers import video, start
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def create_session():
    return AiohttpSession(timeout=10)
async def start_handler(message: Message, bot: Bot):
    await message.answer("🟢 Бот работает!\n🎬 Отправь ссылку на видео")
async def main():
    logger.info("🚀 Запуск бота...")
    session = create_session()
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()
    dp.message.register(start_handler, Command("start"))
    dp.include_router(video.router) 
    try:
        me = await bot.get_me()
        logger.info(f"✅ Авторизован: @{me.username}")
        logger.info("📡 Ожидание сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {type(e).__name__}: {e}")
    finally:
        await bot.close()
if __name__ == "__main__":
    asyncio.run(main())