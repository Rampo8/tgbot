from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from utils.enhancer import enhance_photo, remove_background
from utils.subscription import check_subscription, get_subscribe_keyboard, SUBSCRIBE_MESSAGE
from config import DOWNLOAD_DIR
import os
import asyncio
from handlers.start import UserMode

router = Router()

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

@router.message(F.photo, StateFilter(UserMode.photo))
async def handle_photo(message: types.Message, state: FSMContext):
    # Проверка подписки
    if not await check_sub_required(message, state):
        return
    
    wait_msg = await message.answer("⏳ *Увеличиваю фото...*\n\n"
                                    "Каждый пиксель будет увеличен в 8 раз",
                                    parse_mode="Markdown")
    
    try:
        photo = message.photo[-1]
        
        file = await message.bot.get_file(photo.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, file.file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        await message.bot.download_file(file.file_path, file_path)
        
        original_size = os.path.getsize(file_path)
        
        await wait_msg.edit_text("⏳ *Обрабатываю...*")
        
        enhanced_path = enhance_photo(file_path)
        
        enhanced_size = os.path.getsize(enhanced_path)
        
        await wait_msg.edit_text("✅ *Готово! Отправляю...*")
        
        await message.answer_photo(
            photo=types.FSInputFile(enhanced_path),
            caption=(
                "✨ *Фото увеличено!*\n\n"
                f"📦 Исходный размер: `{original_size // 1024} КБ`\n"
                f"📦 Новый размер: `{enhanced_size // 1024} КБ`\n\n"
                "🔧 *Применено:*\n"
                "• Увеличение в 8 раз (Nearest Neighbor)"
            ),
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(enhanced_path):
            os.remove(enhanced_path)
        
        await wait_msg.delete()
        
    except FileNotFoundError as e:
        await message.answer(
            "❌ *Ошибка: Файл не найден*\n\n"
            "Попробуйте отправить фото ещё раз.",
            parse_mode="Markdown"
        )
        try:
            await wait_msg.delete()
        except:
            pass
        
    except Exception as e:
        error_text = (
            "❌ *Ошибка обработки фото*\n\n"
            f"`{str(e)[:200]}`\n\n"
            "💡 *Возможные причины:*\n"
            "• Повреждённый файл\n"
            "• Неподдерживаемый формат\n"
            "• Недостаточно памяти"
        )
        
        await message.answer(
            text=error_text,
            parse_mode="Markdown"
        )
        
        try:
            await wait_msg.delete()
        except:
            pass
        
        cleanup_photo_files()


@router.message(F.photo, StateFilter(UserMode.bg_remove))
async def handle_bg_remove(message: types.Message, state: FSMContext):
    # Проверка подписки
    if not await check_sub_required(message, state):
        return
    
    wait_msg = await message.answer("⏳ *Убираю задний фон...*\n\n"
                                    "Это может занять некоторое время",
                                    parse_mode="Markdown")

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, file.file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await message.bot.download_file(file.file_path, file_path)

        await wait_msg.edit_text("⏳ *Обрабатываю...*")

        result_path = remove_background(file_path)

        await wait_msg.edit_text("✅ *Готово! Отправляю...*")

        await message.answer_photo(
            photo=types.FSInputFile(result_path),
            caption="✨ *Фон удалён!*",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(result_path):
            os.remove(result_path)

        await wait_msg.delete()

    except Exception as e:
        await message.answer(
            f"❌ *Ошибка:* `{str(e)[:200]}`",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        try:
            await wait_msg.delete()
        except:
            pass


def is_image_document(document):
    image_mime_types = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
        'image/bmp'
    ]
    return document.mime_type in image_mime_types


def cleanup_photo_files():
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            if filename.startswith('enhanced_') or filename.endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Ошибка очистки фото: {e}")