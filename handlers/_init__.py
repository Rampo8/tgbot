# Этот файл делает папку handlers Python-пакетом
# Через него импортируются все обработчики (роутеры)

from . import video
from . import photo
from . import start

__all__ = [
    "video",
    "photo",
    "start"
]