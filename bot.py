import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, LOG_LEVEL
from handlers import video, start, photo
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def create_session():
    return AiohttpSession(timeout=10)
async def main():
    logger.info("🚀 Запуск бота...")
    session = create_session()
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(video.router)
    dp.include_router(photo.router)
    dp.include_router(start.router)
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