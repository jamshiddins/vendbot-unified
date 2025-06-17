from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import AsyncSessionLocal
from core.services.user_service import UserService
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    # Очищаем состояние
    await state.clear()
    
    # Получаем или создаем пользователя
    async with AsyncSessionLocal() as db:
        service = UserService(db)
        
        # Проверяем существующего пользователя
        user = await service.get_user_by_telegram(message.from_user.id)
        
        if not user:
            # Создаем нового пользователя
            from api.schemas import UserCreate
            user_data = UserCreate(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            user = await service.create_user(user_data)
            
            await message.answer(
                f"👋 Добро пожаловать в VendBot!\n\n"
                f"Вы зарегистрированы как: {user.full_name}\n"
                f"Роль: {user.role.value}\n\n"
                f"Обратитесь к администратору для назначения нужной роли."
            )
        else:
            # Показываем главное меню в зависимости от роли
            keyboard = get_main_menu(user.role)
            await message.answer(
                f"👋 С возвращением, {user.full_name}!\n\n"
                f"Ваша роль: {user.role.value}\n"
                f"Выберите действие:",
                reply_markup=keyboard
            )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📚 **Помощь по VendBot**

Доступные команды:
/start - Главное меню
/help - Эта справка
/profile - Ваш профиль

В зависимости от вашей роли вам доступны различные функции:

👤 **Оператор**: работа с бункерами и машинами
📦 **Склад**: управление запасами и назначениями
🚛 **Водитель**: маршруты и доставки
👑 **Админ**: полный доступ к системе

Для навигации используйте кнопки меню.
"""
    await message.answer(help_text, parse_mode="Markdown")