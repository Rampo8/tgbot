import subprocess
import os
import logging
from pathlib import Path
from config import DOWNLOAD_DIR, VIDEO_TARGET_SIZE, VIDEO_SPLIT_CHUNK

logger = logging.getLogger(__name__)

# Лимит Telegram для ботов
TELEGRAM_FILE_LIMIT = VIDEO_SPLIT_CHUNK  # 50 МБ
TARGET_FILE_SIZE = VIDEO_TARGET_SIZE  # 45 МБ целевой размер


def compress_video(input_path: str, max_height: int = 720) -> str:
    """
    Сжимает видео с помощью FFmpeg.
    
    Args:
        input_path: Путь к исходному видео
        max_height: Максимальная высота видео (720p, 480p и т.д.)
        
    Returns:
        str: Путь к сжатому видео
    """
    base = Path(input_path)
    output_path = base.parent / f"compressed_{base.stem}.mp4"
    
    # Получаем информацию о видео
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration,bit_rate',
        '-of', 'json',
        input_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        import json
        info = json.loads(result.stdout)['streams'][0]
        
        width = info.get('width', 1280)
        height = info.get('height', 720)
        duration = float(info.get('duration', 60))
        
        # Рассчитываем целевой битрейт для получения файла ~45 МБ
        # Размер = битрейт * длительность
        target_bitrate = int((TARGET_FILE_SIZE * 8) / duration)
        
        # Ограничиваем минимальный битрейт
        target_bitrate = max(target_bitrate, 500_000)  # Минимум 500 kbps
        
        logger.info(f"Исходное: {width}x{height}, битрейт: {info.get('bit_rate', 'N/A')}")
        logger.info(f"Целевой битрейт: {target_bitrate // 1000} kbps")
        
        # Сжимаем видео
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'scale=-2:{min(height, max_height)}',
            '-c:v', 'libx264',
            '-b:v', str(target_bitrate),
            '-c:a', 'aac',
            '-b:a', '128k',
            '-preset', 'medium',
            '-movflags', '+faststart',
            '-y',
            str(output_path)
        ]
        
        logger.info(f"Запуск сжатия: {output_path}")
        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, encoding='utf-8')
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Сжато: {size_mb:.2f} МБ")
            return str(output_path)
        else:
            raise Exception("FFmpeg не создал файл")
            
    except Exception as e:
        logger.error(f"Ошибка сжатия: {e}")
        raise Exception(f"Ошибка сжатия видео: {str(e)}")


def split_file(input_path: str, chunk_size: int = TELEGRAM_FILE_LIMIT) -> list:
    """
    Разбивает файл на части.
    
    Args:
        input_path: Путь к файлу
        chunk_size: Размер каждой части в байтах
        
    Returns:
        list: Список путей к частям файла
    """
    file_size = os.path.getsize(input_path)
    
    if file_size <= chunk_size:
        return [input_path]
    
    parts = []
    base = Path(input_path)
    
    with open(input_path, 'rb') as f:
        part_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            part_path = base.parent / f"{base.stem}.part{part_num:03d}{base.suffix}"
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            parts.append(str(part_path))
            part_num += 1
            logger.info(f"Создана часть {part_num}: {part_path}")
    
    logger.info(f"Файл разбит на {len(parts)} частей")
    return parts


def process_video(input_path: str, max_height: int = 720) -> tuple:
    """
    Обрабатывает видео: сжатие + разбиение при необходимости.

    Args:
        input_path: Путь к исходному видео
        max_height: Максимальная высота видео

    Returns:
        tuple: (список путей к файлам, название, было_сжато)
    """
    file_size = os.path.getsize(input_path)
    was_compressed = False
    original_path = input_path

    # Если файл больше лимита - сжимаем
    if file_size > TELEGRAM_FILE_LIMIT:
        logger.info(f"Файл больше 50 МБ ({file_size // (1024*1024)} МБ), сжимаем...")
        try:
            compressed_path = compress_video(input_path, max_height)
            was_compressed = True

            # Проверяем размер после сжатия
            compressed_size = os.path.getsize(compressed_path)

            # Если сжатие помогло - удаляем оригинал
            if compressed_size < file_size:
                os.remove(input_path)
                input_path = compressed_path
                file_size = compressed_size
                logger.info(f"Сжатие успешно: {compressed_size // (1024*1024)} МБ")
            else:
                # Сжатие не помогло - удаляем сжатый файл
                os.remove(compressed_path)
                logger.info("Сжатие не помогло, используем оригинал")

        except Exception as e:
            logger.error(f"Ошибка сжатия: {e}")
            raise

    # Если после сжатия всё ещё больше лимита - разбиваем на части
    if file_size > TELEGRAM_FILE_LIMIT:
        logger.info(f"Разбиение на части...")
        parts = split_file(input_path, TELEGRAM_FILE_LIMIT - 1024 * 100)  # Запас 100 КБ
        # Удаляем сжатый файл после разбиения
        if input_path != original_path and os.path.exists(input_path):
            os.remove(input_path)
        return parts, Path(original_path).stem.replace('compressed_', ''), was_compressed

    return [input_path], Path(input_path).stem.replace('compressed_', ''), was_compressed


def cleanup_files(paths: list):
    """Удаляет временные файлы."""
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Удалён файл: {path}")
        except Exception as e:
            logger.error(f"Ошибка удаления {path}: {e}")
