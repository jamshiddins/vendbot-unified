import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from core.config import settings

# Создаем директорию для логов
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

def setup_logging():
    """Настройка системы логирования"""
    
    # Формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                log_dir / "vendbot.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Отдельный файл для ошибок
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    logging.getLogger().addHandler(error_handler)
    
    # Настройка логгеров для библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    
    # Логгер для аудита операций
    audit_logger = logging.getLogger("audit")
    audit_handler = RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    audit_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - USER:%(user_id)s - %(message)s",
        date_format
    ))
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

# Инициализация при импорте
logger = setup_logging()