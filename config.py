import os

# Токен бота
BOT_TOKEN = "8669841170:AAGLNDcki7hVM6p6hAQQkzmzWmwVQnZ5H9o"

# Папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Лимит файла: 50 МБ
MAX_FILE_SIZE = 50 * 1024 * 1024

# Качество видео
VIDEO_MAX_HEIGHT = 480

# Настройки улучшения фото
PHOTO_ENHANCE_SHARPNESS = 1.5
PHOTO_ENHANCE_CONTRAST = 1.2
PHOTO_ENHANCE_BRIGHTNESS = 1.1
PHOTO_SAVE_QUALITY = 95

# Логирование
LOG_LEVEL = "INFO"