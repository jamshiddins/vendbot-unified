import redis.asyncio as redis
from core.config import settings

async def create_redis_pool():
    '''Создание пула подключений к Redis'''
    try:
        # Если Redis URL не указан, возвращаем None
        if not settings.redis_url or settings.redis_url == 'redis://localhost:6379/0':
            print(' Redis не настроен, работаем без кэша')
            return None
            
        pool = await redis.from_url(
            settings.redis_url,
            encoding='utf-8',
            decode_responses=True
        )
        
        # Проверяем подключение
        await pool.ping()
        print('✅ Подключение к Redis установлено')
        return pool
        
    except Exception as e:
        print(f' Не удалось подключиться к Redis: {e}')
        print('Продолжаем работу без кэша')
        return None
