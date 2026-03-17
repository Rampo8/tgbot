# utils/downloader.py
import yt_dlp
import os
from config import DOWNLOAD_DIR

def download_video(url):
    """Скачивает видео и возвращает путь к файлу"""
    ydl_opts = {
        'format': 'best[height<=720]',  # Ограничиваем качество для экономии места
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Video')
    except Exception as e:
        raise Exception(f"Ошибка загрузки: {str(e)}")