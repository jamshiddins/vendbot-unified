from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from db.database import AsyncSessionLocal
from db.models.user import UserRole
from core.services.user_service import UserService
from bot.filters import RoleFilter
from api.websocket import ws_manager

router = Router(name="driver_route")

@router.message(F.text == "🚛 Маршрут", RoleFilter(UserRole.DRIVER))
async def show_route(message: Message, state: FSMContext):
    """Показ маршрута на сегодня"""
    await state.clear()
    
    # Демо маршрут
    route_points = [
        {
            "id": 1,
            "name": "ТЦ Мега Планет",
            "address": "ул. Амира Темура, 41",
            "machines": 3,
            "priority": 1,
            "status": "pending"
        },
        {
            "id": 2,
            "name": "Бизнес-центр Пойтахт",
            "address": "ул. Бухара, 10",
            "machines": 2,
            "priority": 2,
            "status": "pending"
        },
        {
            "id": 3,
            "name": "ТРЦ Сайрам",
            "address": "ул. Катартал, 28",
            "machines": 4,
            "priority": 3,
            "status": "pending"
        }
    ]
    
    await state.update_data(route_points=route_points, current_point=0)
    
    text = f"🗓 **Маршрут на {date.today().strftime('%d.%m.%Y')}**\n\n"
    text += f"📍 Всего точек: {len(route_points)}\n"
    text += f"☕ Всего машин: {sum(p['machines'] for p in route_points)}\n\n"
    
    for i, point in enumerate(route_points, 1):
        status_emoji = "✅" if point['status'] == 'completed' else "⏳"
        text += f"{status_emoji} **{i}. {point['name']}**\n"
        text += f"   📍 {point['address']}\n"
        text += f"   ☕ Машин: {point['machines']}\n\n"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="▶️ Начать маршрут", callback_data="start_route")
    keyboard.button(text="📍 Показать на карте", callback_data="show_map")
    keyboard.adjust(1)
    
    await message.answer(
        text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "start_route")
async def start_route(callback: CallbackQuery, state: FSMContext):
    """Начало маршрута"""
    data = await state.get_data()
    route_points = data.get('route_points', [])
    
    if not route_points:
        await callback.answer("Маршрут пуст")
        return
    
    current_point = route_points[0]
    await state.update_data(current_point=0, start_time=datetime.now())
    
    text = f"🚛 **Маршрут начат!**\n\n"
    text += f"➡️ Следующая точка:\n"
    text += f"**{current_point['name']}**\n"
    text += f"📍 {current_point['address']}\n"
    text += f"☕ Машин: {current_point['machines']}\n\n"
    text += f"Время начала: {datetime.now().strftime('%H:%M')}"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Прибыл на точку", callback_data="arrived")
    keyboard.button(text="📍 Навигация", callback_data=f"navigate:{current_point['id']}")
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "arrived")
async def arrived_at_point(callback: CallbackQuery, state: FSMContext):
    """Прибытие на точку"""
    data = await state.get_data()
    current_idx = data.get('current_point', 0)
    route_points = data.get('route_points', [])
    
    if current_idx >= len(route_points):
        await callback.answer("Маршрут завершен")
        return
    
    current_point = route_points[current_idx]
    
    # Отмечаем время прибытия
    arrival_time = datetime.now()
    await state.update_data(arrival_time=arrival_time)
    
    text = f"✅ **Прибыли в {current_point['name']}**\n\n"
    text += f"⏱ Время прибытия: {arrival_time.strftime('%H:%M')}\n"
    text += f"☕ Обслужить машин: {current_point['machines']}\n\n"
    text += "Начните обслуживание машин"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📦 Пополнить машину", callback_data="refill_machine")
    keyboard.button(text="✅ Завершить точку", callback_data="complete_point")
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    
    # Уведомляем через WebSocket
    async with AsyncSessionLocal() as db:
        user_service = UserService(db)
        driver = await user_service.get_user_by_telegram(callback.from_user.id)
        
        await ws_manager.broadcast_to_role({
            'type': 'driver_arrived',
            'driver_id': driver.id,
            'driver_name': driver.full_name or driver.username,
            'location': current_point['name'],
            'timestamp': arrival_time.isoformat()
        }, 'admin')

@router.callback_query(F.data == "complete_point")
async def complete_point(callback: CallbackQuery, state: FSMContext):
    """Завершение точки"""
    data = await state.get_data()
    current_idx = data.get('current_point', 0)
    route_points = data.get('route_points', [])
    
    # Отмечаем точку как выполненную
    route_points[current_idx]['status'] = 'completed'
    current_idx += 1
    
    if current_idx >= len(route_points):
        # Маршрут завершен
        start_time = data.get('start_time', datetime.now())
        duration = datetime.now() - start_time
        
        text = f"🎉 **Маршрут завершен!**\n\n"
        text += f"📍 Пройдено точек: {len(route_points)}\n"
        text += f"⏱ Общее время: {duration.seconds // 3600}ч {(duration.seconds % 3600) // 60}мин\n"
        text += f"☕ Обслужено машин: {sum(p['machines'] for p in route_points)}\n\n"
        text += "Отличная работа! 👏"
        
        await callback.message.edit_text(text, parse_mode="Markdown")
        await state.clear()
    else:
        # Следующая точка
        next_point = route_points[current_idx]
        await state.update_data(current_point=current_idx, route_points=route_points)
        
        text = f"✅ Точка завершена!\n\n"
        text += f"➡️ Следующая точка:\n"
        text += f"**{next_point['name']}**\n"
        text += f"📍 {next_point['address']}\n"
        text += f"☕ Машин: {next_point['machines']}\n"
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🚛 Ехать дальше", callback_data="arrived")
        keyboard.button(text="📍 Навигация", callback_data=f"navigate:{next_point['id']}")
        keyboard.adjust(1)
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )