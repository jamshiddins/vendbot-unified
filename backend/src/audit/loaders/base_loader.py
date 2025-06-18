from abc import ABC, abstractmethod
from typing import List, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseLoader(ABC):
    """Базовый класс для загрузчиков данных"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
    
    @abstractmethod
    def load(self) -> List[Any]:
        """Загрузка данных из файла"""
        pass
    
    def validate_headers(self, headers: List[str], required: List[str]):
        """Проверка наличия обязательных колонок"""
        missing = set(required) - set(headers)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")