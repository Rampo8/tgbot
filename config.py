import os
BOT_TOKEN = "8669841170:AAGLNDcki7hVM6p6hAQQkzmzWmwVQnZ5H9o"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024
VIDEO_MAX_HEIGHT = 720
PHOTO_ENHANCE_SHARPNESS = 1.5
PHOTO_ENHANCE_CONTRAST = 1.2
PHOTO_ENHANCE_BRIGHTNESS = 1.1
PHOTO_SAVE_QUALITY = 95
LOG_LEVEL = "INFO"

# Настройки процессора видео
VIDEO_TARGET_SIZE = 45 * 1024 * 1024  # Целевой размер после сжатия (45 МБ с запасом)
VIDEO_SPLIT_CHUNK = 50 * 1024 * 1024  # Размер части для разбиения (50 МБ)