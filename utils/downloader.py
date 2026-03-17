import yt_dlp
import os
from config import DOWNLOAD_DIR, VIDEO_MAX_HEIGHT

def download_video(url):
    """
    Скачивает видео с YouTube, Rutube, Instagram и других сайтов.
    Возвращает путь к файлу и название видео.
    """
    ydl_opts = {
        # Формат: лучшее видео до указанной высоты + лучшее аудио
        'format': f'bestvideo[height<={VIDEO_MAX_HEIGHT}]+bestaudio/best[height<={VIDEO_MAX_HEIGHT}]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'socket_timeout': 30,
        'retries': 3,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию и скачиваем
            info = ydl.extract_info(url, download=True)
            
            # Получаем путь к файлу
            filename = ydl.prepare_filename(info)
            
            # Если файл имеет другой формат после конвертации, ищем его
            if not os.path.exists(filename):
                # Пробуем найти файл с расширением .mp4
                base_name = os.path.splitext(filename)[0]
                for ext in ['.mp4', '.mkv', '.webm', '.avi']:
                    test_path = base_name + ext
                    if os.path.exists(test_path):
                        filename = test_path
                        break
            
            # Получаем название видео
            title = info.get('title', 'Video')
            
            return filename, title
            
    except yt_dlp.utils.DownloadError as e:
        raise Exception(f"Ошибка загрузки: {str(e)}")
    except Exception as e:
        raise Exception(f"Неизвестная ошибка: {str(e)}")