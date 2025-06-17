# backend/bot/main.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

class UnifiedBot:
    def __init__(self, api_client):
        self.api = api_client  # Использует те же API что и веб/мобайл
        self.bot = Bot(token=settings.BOT_TOKEN)
        self.storage = RedisStorage.from_url(settings.REDIS_URL)
        self.dp = Dispatcher(storage=self.storage)
        
    async def hopper_fill_handler(self, message: Message, state: FSMContext):
        """Заполнение бункера через Telegram"""
        # Собираем данные через диалог
        data = await self.collect_hopper_data(message, state)
        
        # Используем единый API
        result = await self.api.post("/api/v2/hopper-operations", 
                                    json=data,
                                    headers={"channel": "telegram"})
        
        await message.answer(f"✅ Операция записана: {result['id']}")