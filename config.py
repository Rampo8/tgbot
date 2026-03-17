import os

BOT_TOKEN = "8669841170:AAGLNDcki7hVM6p6hAQQkzmzWmwVQnZ5H9o"

# Папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Ограничения Telegram
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
