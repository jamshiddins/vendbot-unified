from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional

from bot.filters import OwnerFilter
from db.models.user import User, UserRole, UserRoleAssignment
from db.database import AsyncSessionLocal

router = Router()

class RoleAssignStates(StatesGroup):
    waiting_for_user = State()
    selecting_role = State()

def get_role_keyboard(user_roles: list = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора ролей"""
    if user_roles is None:
        user_roles = []
    
    buttons = []
    role_names = {
        UserRole.ADMIN: " Администратор",
        UserRole.WAREHOUSE: " Склад",
        UserRole.OPERATOR: " Оператор",
        UserRole.DRIVER: " Водитель"
    }
    
    for role in UserRole:
        status = "" if role in user_roles else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {role_names[role]}",
                callback_data=f"toggle_role:{role.value}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=" Сохранить", callback_data="save_roles"),
        InlineKeyboardButton(text=" Отмена", callback_data="cancel_roles")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(Command("role"), OwnerFilter())
async def cmd_role_owner(message: Message, state: FSMContext):
    """Команда /role - только для владельца"""
    await message.answer(
        " <b>Управление ролями</b>\n\n"
        "Отправьте username или ID пользователя для назначения ролей.\n"
        "Например: @username или 123456789",
        parse_mode="HTML"
    )
    await state.set_state(RoleAssignStates.waiting_for_user)

@router.message(RoleAssignStates.waiting_for_user)
async def process_user_input(message: Message, state: FSMContext):
    """Обработка ввода пользователя"""
    text = message.text.strip()
    
    async with AsyncSessionLocal() as session:
        # Поиск по username или telegram_id
        if text.startswith("@"):
            username = text[1:]
            user = await session.scalar(
                select(User).where(User.username == username)
            )
        else:
            try:
                telegram_id = int(text)
                user = await session.scalar(
                    select(User).where(User.telegram_id == telegram_id)
                )
            except ValueError:
                await message.answer(" Неверный формат. Используйте @username или ID")
                return
        
        if not user:
            await message.answer(" Пользователь не найден в системе")
            return
        
        # Загружаем роли пользователя
        await session.refresh(user, ["roles"])
        
        # Получаем текущие роли
        current_roles = user.get_roles()
        
        await state.update_data(user_id=user.id, current_roles=current_roles)
        await state.set_state(RoleAssignStates.selecting_role)
        
        await message.answer(
            f" <b>Пользователь:</b> {user.full_name}\n"
            f" <b>ID:</b> {user.telegram_id}\n"
            f" <b>Username:</b> @{user.username or 'не указан'}\n\n"
            "Выберите роли для пользователя:",
            parse_mode="HTML",
            reply_markup=get_role_keyboard(current_roles)
        )

@router.callback_query(F.data.startswith("toggle_role:"))
async def toggle_role(callback: CallbackQuery, state: FSMContext):
    """Переключение роли"""
    role_value = callback.data.split(":")[1]
    role = UserRole(role_value)
    
    data = await state.get_data()
    current_roles = data.get("current_roles", [])
    
    if role in current_roles:
        current_roles.remove(role)
    else:
        current_roles.append(role)
    
    await state.update_data(current_roles=current_roles)
    await callback.message.edit_reply_markup(
        reply_markup=get_role_keyboard(current_roles)
    )
    await callback.answer()

@router.callback_query(F.data == "save_roles")
async def save_roles(callback: CallbackQuery, state: FSMContext):
    """Сохранение ролей"""
    data = await state.get_data()
    user_id = data["user_id"]
    new_roles = data["current_roles"]
    
    async with AsyncSessionLocal() as session:
        # Получаем пользователя с его ролями
        user = await session.get(User, user_id)
        await session.refresh(user, ["roles"])
        
        # Деактивируем все текущие роли
        for role_assignment in user.roles:
            role_assignment.is_active = False
        
        # Назначаем новые роли
        for role in new_roles:
            # Проверяем, есть ли уже такая роль
            existing = next(
                (r for r in user.roles if r.role == role), 
                None
            )
            
            if existing:
                existing.is_active = True
            else:
                new_assignment = UserRoleAssignment(
                    user_id=user_id,
                    role=role,
                    assigned_by=callback.from_user.id,
                    is_active=True
                )
                session.add(new_assignment)
        
        await session.commit()
    
    await callback.message.edit_text(
        " Роли успешно обновлены!",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "cancel_roles")
async def cancel_roles(callback: CallbackQuery, state: FSMContext):
    """Отмена назначения ролей"""
    await callback.message.edit_text(" Назначение ролей отменено")
    await state.clear()

# Команда /role для обычных пользователей - не показываем
@router.message(Command("role"))
async def cmd_role_others(message: Message):
    """Для всех остальных команда недоступна - просто игнорируем"""
    pass
