from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from db.models import Hopper, HopperStatus, Ingredient, Machine, User, UserRole, HopperOperation, OperationType
from bot.keyboards.inline import get_back_button

router = Router()

class HopperForm(StatesGroup):
    """Состояния для работы с бункерами"""
    number = State()
    weight_empty = State()
    weight_with_lid = State()
    select_ingredient = State()
    weight_full = State()
    select_machine = State()
    operation_notes = State()

def get_hopper_menu(user_role: UserRole) -> InlineKeyboardMarkup:
    """Меню работы с бункерами в зависимости от роли"""
    keyboard = []
    
    if user_role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
        keyboard.extend([
            [InlineKeyboardButton(text=" Все бункеры", callback_data="hoppers_all")],
            [InlineKeyboardButton(text=" Создать бункер", callback_data="hopper_create")],
            [InlineKeyboardButton(text=" Взвесить пустой", callback_data="hopper_weigh_empty")],
            [InlineKeyboardButton(text=" Взвесить с крышкой", callback_data="hopper_weigh_lid")],
            [InlineKeyboardButton(text=" Заполнить ингредиентом", callback_data="hopper_fill")],
        ])
    
    if user_role in [UserRole.ADMIN, UserRole.OPERATOR]:
        keyboard.extend([
            [InlineKeyboardButton(text=" Установить в автомат", callback_data="hopper_install")],
            [InlineKeyboardButton(text=" Снять с автомата", callback_data="hopper_remove")],
            [InlineKeyboardButton(text=" Мои бункеры", callback_data="hoppers_my")],
        ])
    
    keyboard.append([InlineKeyboardButton(text=" История операций", callback_data="hopper_history")])
    keyboard.append([InlineKeyboardButton(text=" Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_hoppers_list_keyboard(hoppers: List[Hopper], action: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком бункеров"""
    keyboard = []
    for hopper in hoppers:
        status_emoji = {
            HopperStatus.EMPTY: "",
            HopperStatus.FILLED: "",
            HopperStatus.INSTALLED: "",
            HopperStatus.CLEANING: "",
            HopperStatus.RETURNED: ""
        }.get(hopper.status, "")
        
        ingredient_name = hopper.ingredient.name if hopper.ingredient else "Пусто"
        text = f"{status_emoji} {hopper.number} - {ingredient_name}"
        
        keyboard.append([InlineKeyboardButton(
            text=text,
            callback_data=f"{action}:{hopper.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text=" Назад", callback_data="hopper_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "hopper_menu")
async def show_hopper_menu(callback: CallbackQuery, session: AsyncSession):
    """Показать меню работы с бункерами"""
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Работа с бункерами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_hopper_menu(user.role),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "hoppers_all")
async def show_all_hoppers(callback: CallbackQuery, session: AsyncSession):
    """Показать все бункеры"""
    result = await session.execute(
        select(Hopper).order_by(Hopper.number)
    )
    hoppers: List[Hopper] = result.scalars().all()
    
    text = " <b>Все бункеры:</b>\n\n"
    
    if not hoppers:
        text += "Бункеры не созданы"
    else:
        for hopper in hoppers:
            status_emoji = {
                HopperStatus.EMPTY: "",
                HopperStatus.FILLED: "",
                HopperStatus.INSTALLED: "",
                HopperStatus.CLEANING: "",
                HopperStatus.RETURNED: ""
            }.get(hopper.status, "")
            
            text += f"{status_emoji} <b>{hopper.number}</b>\n"
            
            if hopper.ingredient:
                text += f"   Ингредиент: {hopper.ingredient.name}\n"
                if hopper.current_weight and hopper.weight_empty:
                    net_weight = hopper.current_weight - hopper.weight_empty
                    text += f"   Нетто: {net_weight:.2f} кг\n"
            
            if hopper.machine:
                text += f"   Установлен: {hopper.machine.code}\n"
            
            if hopper.assigned_to:
                text += f"   Назначен: {hopper.assigned_to.full_name}\n"
            
            text += f"   Статус: {hopper.status.value}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="hopper_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "hopper_create")
async def start_create_hopper(callback: CallbackQuery, state: FSMContext):
    """Начать создание нового бункера"""
    await state.set_state(HopperForm.number)
    
    await callback.message.edit_text(
        " <b>Создание нового бункера</b>\n\n"
        "Введите номер бункера (например: H001):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(HopperForm.number)
async def process_hopper_number(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка номера бункера"""
    number = message.text.strip().upper()
    
    # Проверяем уникальность
    result = await session.execute(
        select(Hopper).where(Hopper.number == number)
    )
    if result.scalar_one_or_none():
        await message.answer(
            " Бункер с таким номером уже существует!\n"
            "Введите другой номер:"
        )
        return
    
    # Создаем бункер
    hopper = Hopper(
        number=number,
        status=HopperStatus.EMPTY
    )
    
    session.add(hopper)
    await session.commit()
    
    await state.clear()
    
    # Создаем запись операции
    operation = HopperOperation(
        operation_type=OperationType.FILL,  # Используем FILL как "создание"
        hopper_id=hopper.id,
        user_id=(await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )).scalar_one().id,
        notes="Бункер создан"
    )
    session.add(operation)
    await session.commit()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Взвесить пустой", callback_data=f"weigh_empty:{hopper.id}")],
        [InlineKeyboardButton(text=" К меню бункеров", callback_data="hopper_menu")]
    ])
    
    await message.answer(
        f" <b>Бункер создан!</b>\n\n"
        f"Номер: {hopper.number}\n"
        f"Статус: Пустой\n\n"
        f"Теперь нужно взвесить пустой бункер",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "hopper_fill")
async def show_empty_hoppers(callback: CallbackQuery, session: AsyncSession):
    """Показать пустые бункеры для заполнения"""
    result = await session.execute(
        select(Hopper).where(
            Hopper.status == HopperStatus.EMPTY,
            Hopper.weight_empty.isnot(None),
            Hopper.weight_with_lid.isnot(None)
        ).order_by(Hopper.number)
    )
    hoppers = result.scalars().all()
    
    if not hoppers:
        await callback.answer(
            "Нет готовых пустых бункеров!\n"
            "Сначала взвесьте пустые бункеры.",
            show_alert=True
        )
        return
    
    await callback.message.edit_text(
        " <b>Выберите бункер для заполнения:</b>\n\n"
        "Показаны только взвешенные пустые бункеры",
        reply_markup=get_hoppers_list_keyboard(hoppers, "fill_hopper"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("fill_hopper:"))
async def select_ingredient_for_hopper(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Выбрать ингредиент для заполнения"""
    hopper_id = int(callback.data.split(":")[1])
    
    # Получаем список ингредиентов
    result = await session.execute(
        select(Ingredient).where(Ingredient.current_stock > 0).order_by(Ingredient.name)
    )
    ingredients = result.scalars().all()
    
    if not ingredients:
        await callback.answer("Нет доступных ингредиентов на складе!", show_alert=True)
        return
    
    await state.update_data(hopper_id=hopper_id)
    
    keyboard = []
    for ing in ingredients:
        text = f"{ing.name} ({ing.current_stock:.1f} {ing.unit})"
        keyboard.append([InlineKeyboardButton(
            text=text,
            callback_data=f"select_ing:{ing.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text=" Отмена", callback_data="hopper_menu")])
    
    await callback.message.edit_text(
        " <b>Выберите ингредиент:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_ing:"))
async def process_ingredient_selection(callback: CallbackQuery, state: FSMContext):
    """Обработать выбор ингредиента"""
    ingredient_id = int(callback.data.split(":")[1])
    
    await state.update_data(ingredient_id=ingredient_id)
    await state.set_state(HopperForm.weight_full)
    
    await callback.message.edit_text(
        " <b>Взвесьте заполненный бункер</b>\n\n"
        "Введите вес заполненного бункера (в кг):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(HopperForm.weight_full)
async def process_full_weight(message: Message, state: FSMContext, session: AsyncSession):
    """Обработать вес заполненного бункера"""
    try:
        weight_full = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(" Введите корректный вес (число)!")
        return
    
    data = await state.get_data()
    hopper_id = data['hopper_id']
    ingredient_id = data['ingredient_id']
    
    # Получаем бункер и ингредиент
    hopper = await session.get(Hopper, hopper_id)
    ingredient = await session.get(Ingredient, ingredient_id)
    
    if not hopper or not ingredient:
        await message.answer(" Ошибка: бункер или ингредиент не найден")
        await state.clear()
        return
    
    # Рассчитываем вес нетто
    net_weight = weight_full - hopper.weight_with_lid
    
    if net_weight <= 0:
        await message.answer(
            f" Ошибка: вес нетто отрицательный!\n"
            f"Вес полного: {weight_full} кг\n"
            f"Вес с крышкой: {hopper.weight_with_lid} кг"
        )
        return
    
    # Проверяем наличие на складе
    if ingredient.current_stock < net_weight:
        await message.answer(
            f" Недостаточно ингредиента на складе!\n"
            f"Требуется: {net_weight:.2f} кг\n"
            f"Доступно: {ingredient.current_stock:.2f} кг"
        )
        return
    
    # Обновляем бункер
    hopper.ingredient_id = ingredient_id
    hopper.weight_full = weight_full
    hopper.current_weight = weight_full
    hopper.status = HopperStatus.FILLED
    hopper.last_filled_date = datetime.utcnow()
    
    # Списываем со склада
    ingredient.current_stock -= net_weight
    
    # Создаем запись операции
    user = (await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )).scalar_one()
    
    operation = HopperOperation(
        operation_type=OperationType.FILL,
        hopper_id=hopper_id,
        user_id=user.id,
        weight_before=hopper.weight_with_lid,
        weight_after=weight_full,
        notes=f"Заполнен {ingredient.name}: {net_weight:.2f} кг"
    )
    
    session.add(operation)
    await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" К меню бункеров", callback_data="hopper_menu")]
    ])
    
    await message.answer(
        f" <b>Бункер заполнен!</b>\n\n"
        f"Бункер: {hopper.number}\n"
        f"Ингредиент: {ingredient.name}\n"
        f"Вес брутто: {weight_full:.2f} кг\n"
        f"Вес нетто: {net_weight:.2f} кг\n\n"
        f"Списано со склада: {net_weight:.2f} кг",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "hoppers_my")
async def show_my_hoppers(callback: CallbackQuery, session: AsyncSession):
    """Показать бункеры текущего пользователя"""
    user = (await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )).scalar_one()
    
    result = await session.execute(
        select(Hopper).where(
            Hopper.assigned_to_id == user.id
        ).order_by(Hopper.number)
    )
    hoppers = result.scalars().all()
    
    text = " <b>Мои бункеры:</b>\n\n"
    
    if not hoppers:
        text += "У вас нет назначенных бункеров"
    else:
        for hopper in hoppers:
            status_emoji = {
                HopperStatus.EMPTY: "",
                HopperStatus.FILLED: "",
                HopperStatus.INSTALLED: "",
                HopperStatus.CLEANING: "",
                HopperStatus.RETURNED: ""
            }.get(hopper.status, "")
            
            text += f"{status_emoji} <b>{hopper.number}</b>\n"
            
            if hopper.ingredient:
                text += f"   Ингредиент: {hopper.ingredient.name}\n"
            
            if hopper.machine:
                text += f"   Установлен: {hopper.machine.code}\n"
            
            text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="hopper_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# Добавим обработчики для взвешивания
@router.callback_query(F.data == "hopper_weigh_empty")
async def show_hoppers_for_empty_weigh(callback: CallbackQuery, session: AsyncSession):
    """Показать бункеры для взвешивания пустых"""
    result = await session.execute(
        select(Hopper).where(
            Hopper.weight_empty.is_(None)
        ).order_by(Hopper.number)
    )
    hoppers = result.scalars().all()
    
    if not hoppers:
        await callback.answer("Все бункеры уже взвешены", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите бункер для взвешивания:</b>",
        reply_markup=get_hoppers_list_keyboard(hoppers, "weigh_empty"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("weigh_empty:"))
async def start_weigh_empty(callback: CallbackQuery, state: FSMContext):
    """Начать взвешивание пустого бункера"""
    hopper_id = int(callback.data.split(":")[1])
    await state.update_data(weigh_hopper_id=hopper_id, weigh_type="empty")
    await state.set_state(HopperForm.weight_empty)
    
    await callback.message.edit_text(
        " <b>Взвешивание пустого бункера</b>\n\n"
        "Введите вес пустого бункера (в кг):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(HopperForm.weight_empty)
async def process_empty_weight(message: Message, state: FSMContext, session: AsyncSession):
    """Обработать вес пустого бункера"""
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(" Введите корректный вес (число)!")
        return
    
    data = await state.get_data()
    hopper_id = data['weigh_hopper_id']
    
    hopper = await session.get(Hopper, hopper_id)
    if hopper:
        hopper.weight_empty = weight
        await session.commit()
        
        # Создаем запись операции
        user = (await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )).scalar_one()
        
        operation = HopperOperation(
            operation_type=OperationType.WEIGH,
            hopper_id=hopper_id,
            user_id=user.id,
            weight_after=weight,
            notes=f"Взвешен пустой: {weight} кг"
        )
        session.add(operation)
        await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Взвесить с крышкой", callback_data=f"weigh_lid:{hopper_id}")],
        [InlineKeyboardButton(text=" К меню бункеров", callback_data="hopper_menu")]
    ])
    
    await message.answer(
        f" <b>Вес сохранен!</b>\n\n"
        f"Бункер: {hopper.number}\n"
        f"Вес пустого: {weight} кг\n\n"
        f"Теперь нужно взвесить с крышкой",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

__all__ = ["router"]
