import os

def split_file(file_path, chunk_size=49 * 1024 * 1024):
    """
    Разбивает файл на части указанного размера.
    Возвращает список путей к частям.
    
    Args:
        file_path: Путь к исходному файлу
        chunk_size: Размер одной части в байтах (по умолчанию 49 МБ)
    
    Returns:
        List[str]: Список путей к созданным частям
    """
    chunks = []
    file_size = os.path.getsize(file_path)
    chunk_count = (file_size // chunk_size) + 1
    
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # Формируем имя части
            base_name = os.path.basename(file_path)
            chunk_filename = f"{base_name}.part{chunk_num + 1}_of_{chunk_count}"
            chunk_path = os.path.join(os.path.dirname(file_path), chunk_filename)
            
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            chunks.append(chunk_path)
            chunk_num += 1
    
    return chunks


def merge_files(chunk_paths, output_path):
    """
    Объединяет части файлов обратно в один файл.
    
    Args:
        chunk_paths: Список путей к частям (должны быть отсортированы)
        output_path: Путь к выходному файлу
    """
    # Сортируем части по имени (чтобы были в правильном порядке)
    chunk_paths = sorted(chunk_paths)
    
    with open(output_path, 'wb') as outfile:
        for chunk_path in chunk_paths:
            with open(chunk_path, 'rb') as infile:
                outfile.write(infile.read())
            # Удаляем часть после объединения
            os.remove(chunk_path)
    
    return output_path


def get_file_size_human(file_path):
    """
    Возвращает размер файла в человекочитаемом формате.
    """
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.2f} ТБ"