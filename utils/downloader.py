
import yt_dlp
import os
from config import DOWNLOAD_DIR

def download_video(url):
    ydl_opts = {
        'format': 'best[height<=480]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'Video')