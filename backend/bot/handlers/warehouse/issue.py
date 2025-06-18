from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List

from db.database import AsyncSessionLocal
from db.models.user import UserRole, User
from core.services.user_service import UserService
from bot.states import WarehouseIssueStates
from bot.keyboards.inline import get_confirm_keyboard
from bot.filters import RoleFilter
from api.websocket import ws_manager

router = Router(name="warehouse_issue")

@router.message(F.text == "📤 Выдача", RoleFilter(UserRole.WAREHOUSE))
async def start_issue(message: Message, state: FSMContext):
    """Начало процесса выдачи товара"""
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        # Получаем список операторов
        user_service = UserService(db)
        operators = await user_service.get_active_users_by_role(UserRole.OPERATOR)
        
        if not operators:
            await message.answer("❌ Нет активных операторов в системе.")
            return
        
        keyboard = InlineKeyboardBuilder()
        for operator in operators:
            keyboard.button(
                text=f"👤 {operator.full_name or operator.username or f'ID{operator.id}'}",
                callback_data=f"operator:{operator.id}"
            )
        keyboard.button(text="❌ Отмена", callback_data="cancel")
        keyboard.adjust(1)
        
        await message.answer(
            "👥 Выберите оператора для выдачи:",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(WarehouseIssueStates.select_operator)

@router.callback_query(
    WarehouseIssueStates.select_operator,
    F.data.startswith("operator:")
)
async def operator_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора оператора"""
    operator_id = int(callback.data.split(":")[1])
    await state.update_data(operator_id=operator_id)
    
    # Показываем предустановленный набор для выдачи
    preset_items = [
        {"name": "Кофе Арабика", "quantity": 5.0, "unit": "кг"},
        {"name": "Молоко сухое", "quantity": 3.0, "unit": "кг"},
        {"name": "Сахар", "quantity": 2.0, "unit": "кг"},
        {"name": "Стаканы 200мл", "quantity": 1000, "unit": "шт"},
        {"name": "Размешиватели", "quantity": 1000, "unit": "шт"}
    ]
    
    await state.update_data(items=preset_items)
    
    text = "📦 **Стандартный набор для выдачи:**\n\n"
    for item in preset_items:
        text += f"• {item['name']}: {item['quantity']} {item['unit']}\n"
    
    text += "\nВыдать этот набор?"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(WarehouseIssueStates.confirm)

@router.callback_query(
    WarehouseIssueStates.confirm,
    F.data == "confirm:yes"
)
async def confirm_issue(callback: CallbackQuery, state: FSMContext):
    """Подтверждение выдачи"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        # Получаем пользователей
        user_service = UserService(db)
        warehouse_user = await user_service.get_user_by_telegram(callback.from_user.id)
        operator = await user_service.get_user(data['operator_id'])
        
        # Создаем запись о выдаче
        from db.models.inventory import InventoryTransaction, TransactionType
        
        for item in data['items']:
            # Здесь в реальной системе нужно найти ингредиент по имени
            # и проверить достаточность остатков
            transaction = InventoryTransaction(
                ingredient_id=1,  # Заглушка
                transaction_type=TransactionType.ISSUE,
                quantity=-item['quantity'],  # Отрицательное для выдачи
                user_id=warehouse_user.id,
                assigned_to_id=operator.id,
                notes=f"Выдача оператору {operator.full_name or operator.username}"
            )
            db.add(transaction)
        
        await db.commit()
        
        # Уведомляем оператора через WebSocket
        await ws_manager.send_personal_message({
            'type': 'inventory_issued',
            'message': f'Вам выдан набор ингредиентов от склада',
            'items': data['items']
        }, operator.id)
        
        await callback.message.edit_text(
            f"✅ Выдача успешно оформлена!\n\n"
            f"👤 Оператор: {operator.full_name or operator.username}\n"
            f"📦 Выдано позиций: {len(data['items'])}"
        )
    
    await state.clear()