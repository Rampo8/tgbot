# bot.py
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import video, photo
from aiogram import types
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(video.router)
    dp.include_router(photo.router)
    
    # Команда /start
    @dp.message(lambda msg: msg.text == "/start")
    async def start_cmd(message: types.Message):
        await message.answer(
            "👋 Привет! Я бот для работы с медиа.\n\n"
            "🎬 **Видео:** Отправь ссылку на YouTube, Rutube или Instagram\n"
            "📸 **Фото:** Отправь фото, и я улучшу его качество\n\n"
            "Начинай!"
        )
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())