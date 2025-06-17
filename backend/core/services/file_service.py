import os
import uuid
from pathlib import Path
from typing import Optional, List
from PIL import Image
import io
from datetime import datetime
from core.config import settings

class FileService:
    """Сервис для работы с файлами"""
    
    def __init__(self):
        self.upload_path = Path(settings.UPLOAD_PATH)
        self.photos_path = self.upload_path / "photos"
        self.photos_path.mkdir(parents=True, exist_ok=True)
    
    async def save_photo(self, photo_data: bytes, prefix: str = "photo") -> str:
        """Сохранение фотографии"""
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{prefix}_{timestamp}_{unique_id}.jpg"
        
        # Путь для сохранения
        file_path = self.photos_path / filename
        
        # Обрабатываем изображение
        image = Image.open(io.BytesIO(photo_data))
        
        # Изменяем размер если слишком большое
        max_size = (1920, 1920)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в RGB если нужно
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # Сохраняем с оптимизацией
        image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        # Возвращаем относительный путь
        return f"/photos/{filename}"
    
    async def save_multiple_photos(
        self, 
        photos_data: List[bytes], 
        prefix: str = "photo"
    ) -> List[str]:
        """Сохранение нескольких фотографий"""
        saved_paths = []
        for photo_data in photos_data:
            path = await self.save_photo(photo_data, prefix)
            saved_paths.append(path)
        return saved_paths
    
    def get_photo_path(self, photo_url: str) -> Optional[Path]:
        """Получение полного пути к фотографии"""
        if photo_url.startswith("/photos/"):
            filename = photo_url.replace("/photos/", "")
            file_path = self.photos_path / filename
            if file_path.exists():
                return file_path
        return None
    
    async def delete_photo(self, photo_url: str) -> bool:
        """Удаление фотографии"""
        file_path = self.get_photo_path(photo_url)
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        return False

file_service = FileService()