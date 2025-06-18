from fastapi import Request
from datetime import datetime
import time
import psutil
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Мониторинг системных метрик"""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Получение системных метрик"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def log_request(request: Request, response_time: float, status_code: int):
        """Логирование запроса"""
        logger.info(
            f"REQUEST - Method: {request.method} - "
            f"Path: {request.url.path} - "
            f"Status: {status_code} - "
            f"Time: {response_time:.3f}s - "
            f"IP: {request.client.host}"
        )

async def monitor_performance(request: Request, call_next):
    """Middleware для мониторинга производительности"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Логируем медленные запросы
    if process_time > 1.0:
        logger.warning(
            f"SLOW REQUEST - {request.method} {request.url.path} - {process_time:.3f}s"
        )
    
    # Асинхронное логирование
    asyncio.create_task(
        SystemMonitor.log_request(request, process_time, response.status_code)
    )
    
    return response