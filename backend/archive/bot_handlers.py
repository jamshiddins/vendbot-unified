from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в VendBot!\n\n"
        "Я помогу вам управлять вендинговой сетью.\n\n"
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/help - Помощь\n"
        "/status - Статус системы"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 Помощь по VendBot\n\n"
        "Основные команды:\n"
        "/start - Начало работы\n"
        "/help - Эта справка\n"
        "/status - Статус системы\n\n"
        "Для администраторов:\n"
        "/admin - Панель администратора"
    )

@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(
        "✅ Система работает нормально\n\n"
        "🤖 Бот: Активен\n"
        "🗄 База данных: Подключена\n"
        "🌐 API: http://localhost:8000"
    )

# Обработчик всех остальных сообщений
@router.message()
async def echo_message(message: Message):
    await message.answer(
        "❓ Я не понимаю эту команду.\n"
        "Используйте /help для списка доступных команд."
    )
