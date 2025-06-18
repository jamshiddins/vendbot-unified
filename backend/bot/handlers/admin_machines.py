from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.models import Machine
from bot.keyboards.inline import get_back_button

router = Router()

class MachineForm(StatesGroup):
    """Состояния для добавления/редактирования автомата"""
    code = State()
    name = State()
    location = State()
    edit_field = State()
    edit_value = State()

def get_machine_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления автоматами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Список автоматов", callback_data="machines_list")],
        [InlineKeyboardButton(text=" Добавить автомат", callback_data="machine_add")],
        [InlineKeyboardButton(text=" Редактировать автомат", callback_data="machine_edit")],
        [InlineKeyboardButton(text=" Удалить автомат", callback_data="machine_delete")],
        [InlineKeyboardButton(text=" Назад", callback_data="main_menu")]
    ])

def get_machines_list_keyboard(machines: List[Machine], action: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком автоматов для выбора"""
    keyboard = []
    for machine in machines:
        status = "" if machine.status == "active" else ""
        text = f"{status} {machine.code} - {machine.name}"
        keyboard.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"{action}:{machine.id}"
        )])
    keyboard.append([InlineKeyboardButton(text=" Отмена", callback_data="admin_machines")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_machine_edit_keyboard(machine_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора поля редактирования"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Код", callback_data=f"edit_field:{machine_id}:code")],
        [InlineKeyboardButton(text=" Название", callback_data=f"edit_field:{machine_id}:name")],
        [InlineKeyboardButton(text=" Локация", callback_data=f"edit_field:{machine_id}:location")],
        [InlineKeyboardButton(text=" Статус", callback_data=f"toggle_status:{machine_id}")],
        [InlineKeyboardButton(text=" Назад", callback_data="admin_machines")]
    ])

@router.callback_query(F.data == "admin_machines")
async def show_machine_management(callback: CallbackQuery):
    """Показать меню управления автоматами"""
    await callback.message.edit_text(
        " <b>Управление автоматами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_machine_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "machines_list")
async def show_machines_list(callback: CallbackQuery, session: AsyncSession):
    """Показать список всех автоматов"""
    
    result = await session.execute(select(Machine).order_by(Machine.code))
    machines: List[Machine] = result.scalars().all()
    
    text = " <b>Список автоматов:</b>\n\n"
    
    if not machines:
        text += "Автоматы не добавлены"
    else:
        for machine in machines:
            status_emoji = "" if machine.status == "active" else ""
            text += (
                f"{status_emoji} <b>{machine.code}</b>\n"
                f"   Название: {machine.name}\n"
                f"   Локация: {machine.location or 'Не указана'}\n"
                f"   Статус: {machine.status}\n"
                f"   Добавлен: {machine.created_at.strftime('%d.%m.%Y')}\n\n"
            )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад", callback_data="admin_machines")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "machine_add")
async def start_add_machine(callback: CallbackQuery, state: FSMContext):
    """Начать процесс добавления автомата"""
    await state.set_state(MachineForm.code)
    
    await callback.message.edit_text(
        " <b>Добавление нового автомата</b>\n\n"
        "Введите код автомата (например: CVM-004):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(MachineForm.code)
async def process_machine_code(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка кода автомата"""
    code = message.text.strip().upper()
    
    # Проверяем уникальность кода
    result = await session.execute(select(Machine).where(Machine.code == code))
    if result.scalar_one_or_none():
        await message.answer(
            " Автомат с таким кодом уже существует!\n"
            "Введите другой код:"
        )
        return
    
    await state.update_data(code=code)
    await state.set_state(MachineForm.name)
    
    await message.answer(
        f"Код: <b>{code}</b>\n\n"
        "Теперь введите название автомата:",
        parse_mode="HTML"
    )

@router.message(MachineForm.name)
async def process_machine_name(message: Message, state: FSMContext):
    """Обработка названия автомата"""
    await state.update_data(name=message.text.strip())
    await state.set_state(MachineForm.location)
    
    await message.answer(
        "Введите локацию автомата (адрес или описание места):"
    )

@router.message(MachineForm.location)
async def process_machine_location(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка локации и сохранение автомата"""
    data = await state.get_data()
    
    # Создаем новый автомат
    machine = Machine(
        code=data['code'],
        name=data['name'],
        location=message.text.strip(),
        status="active"
    )
    
    session.add(machine)
    await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" К списку автоматов", callback_data="admin_machines")]
    ])
    
    await message.answer(
        f" <b>Автомат успешно добавлен!</b>\n\n"
        f"Код: {machine.code}\n"
        f"Название: {machine.name}\n"
        f"Локация: {machine.location}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "machine_edit")
async def show_machines_for_edit(callback: CallbackQuery, session: AsyncSession):
    """Показать автоматы для редактирования"""
    
    result = await session.execute(select(Machine).order_by(Machine.code))
    machines: List[Machine] = result.scalars().all()
    
    if not machines:
        await callback.answer("Нет автоматов для редактирования", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите автомат для редактирования:</b>",
        reply_markup=get_machines_list_keyboard(machines, "edit_machine"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_machine:"))
async def show_edit_options(callback: CallbackQuery, session: AsyncSession):
    """Показать опции редактирования для автомата"""
    machine_id = int(callback.data.split(":")[1])
    
    machine = await session.get(Machine, machine_id)
    if not machine:
        await callback.answer("Автомат не найден", show_alert=True)
        return
    
    status_emoji = "" if machine.status == "active" else ""
    
    await callback.message.edit_text(
        f" <b>Редактирование автомата</b>\n\n"
        f"Код: {machine.code}\n"
        f"Название: {machine.name}\n"
        f"Локация: {machine.location or 'Не указана'}\n"
        f"Статус: {status_emoji} {machine.status}\n\n"
        f"Выберите что изменить:",
        reply_markup=get_machine_edit_keyboard(machine_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_status:"))
async def toggle_machine_status(callback: CallbackQuery, session: AsyncSession):
    """Переключить статус автомата"""
    machine_id = int(callback.data.split(":")[1])
    
    machine = await session.get(Machine, machine_id)
    if machine:
        machine.status = "inactive" if machine.status == "active" else "active"
        await session.commit()
        
        await callback.answer(f" Статус изменен на {machine.status}")
        await show_edit_options(callback, session)
    else:
        await callback.answer("Автомат не найден", show_alert=True)

@router.callback_query(F.data.startswith("edit_field:"))
async def start_edit_field(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование поля"""
    _, machine_id, field = callback.data.split(":")
    
    await state.update_data(edit_machine_id=int(machine_id), edit_field=field)
    await state.set_state(MachineForm.edit_value)
    
    field_names = {
        "code": "код",
        "name": "название",
        "location": "локацию"
    }
    
    await callback.message.edit_text(
        f" Введите новое значение для поля '{field_names[field]}':",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(MachineForm.edit_value)
async def process_edit_value(message: Message, state: FSMContext, session: AsyncSession):
    """Обработать новое значение поля"""
    data = await state.get_data()
    machine_id = data['edit_machine_id']
    field = data['edit_field']
    new_value = message.text.strip()
    
    machine = await session.get(Machine, machine_id)
    if not machine:
        await message.answer(" Автомат не найден")
        await state.clear()
        return
    
    # Проверка уникальности кода
    if field == "code":
        new_value = new_value.upper()
        result = await session.execute(
            select(Machine).where(Machine.code == new_value, Machine.id != machine_id)
        )
        if result.scalar_one_or_none():
            await message.answer(" Автомат с таким кодом уже существует!")
            return
    
    setattr(machine, field, new_value)
    await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" К списку автоматов", callback_data="admin_machines")]
    ])
    
    await message.answer(
        f" <b>Автомат успешно обновлен!</b>\n\n"
        f"Поле '{field}' изменено на: {new_value}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "machine_delete")
async def show_machines_for_delete(callback: CallbackQuery, session: AsyncSession):
    """Показать автоматы для удаления"""
    
    result = await session.execute(select(Machine).order_by(Machine.code))
    machines: List[Machine] = result.scalars().all()
    
    if not machines:
        await callback.answer("Нет автоматов для удаления", show_alert=True)
        return
    
    await callback.message.edit_text(
        " <b>Выберите автомат для удаления:</b>\n\n"
        " Внимание! Это действие нельзя отменить!",
        reply_markup=get_machines_list_keyboard(machines, "confirm_delete"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_machine(callback: CallbackQuery, session: AsyncSession):
    """Подтвердить удаление автомата"""
    machine_id = int(callback.data.split(":")[1])
    
    machine = await session.get(Machine, machine_id)
    if not machine:
        await callback.answer("Автомат не найден", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=" Да, удалить", callback_data=f"delete_machine:{machine_id}"),
            InlineKeyboardButton(text=" Отмена", callback_data="admin_machines")
        ]
    ])
    
    await callback.message.edit_text(
        f" <b>Подтверждение удаления</b>\n\n"
        f"Вы действительно хотите удалить автомат?\n\n"
        f"Код: {machine.code}\n"
        f"Название: {machine.name}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete_machine:"))
async def delete_machine(callback: CallbackQuery, session: AsyncSession):
    """Удалить автомат"""
    machine_id = int(callback.data.split(":")[1])
    
    machine = await session.get(Machine, machine_id)
    if machine:
        await session.delete(machine)
        await session.commit()
        
        await callback.answer(" Автомат удален")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=" К управлению автоматами", callback_data="admin_machines")]
        ])
        
        await callback.message.edit_text(
            " <b>Автомат успешно удален!</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.answer("Автомат не найден", show_alert=True)

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    await show_machine_management(callback)

__all__ = ["router"]
