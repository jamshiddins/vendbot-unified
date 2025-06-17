from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import List

from db.database import AsyncSessionLocal
from db.models.asset import AssetType
from db.models.user import UserRole
from core.services.asset_service import AssetService
from core.services.operation_service import OperationService
from core.services.user_service import UserService
from core.services.file_service import file_service
from bot.states import HopperFillStates
from bot.keyboards.inline import (
    get_hoppers_keyboard,
    get_ingredients_keyboard,
    get_machines_keyboard,
    get_confirm_keyboard,
    get_skip_keyboard
)
from bot.filters import RoleFilter

router = Router(name="hopper_fill")

@router.message(F.text == "📦 Заполнить бункер", RoleFilter(UserRole.OPERATOR))
async def start_hopper_fill(message: Message, state: FSMContext):
    """Начало процесса заполнения бункера"""
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        hoppers = await asset_service.get_available_hoppers()
        
        if not hoppers:
            await message.answer(
                "❌ Нет доступных бункеров для заполнения.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        keyboard = get_hoppers_keyboard(hoppers)
        await message.answer(
            "📦 Выберите бункер для заполнения:",
            reply_markup=keyboard
        )
        await state.set_state(HopperFillStates.select_hopper)

@router.callback_query(
    HopperFillStates.select_hopper,
    F.data.startswith("hopper:")
)
async def hopper_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора бункера"""
    hopper_id = int(callback.data.split(":")[1])
    await state.update_data(hopper_id=hopper_id)
    
    # Получаем список ингредиентов
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from db.models.ingredient import Ingredient
        
        result = await db.execute(select(Ingredient))
        ingredients = result.scalars().all()
        
        if not ingredients:
            await callback.message.edit_text(
                "❌ Нет доступных ингредиентов в системе."
            )
            await state.clear()
            return
        
        keyboard = get_ingredients_keyboard(ingredients)
        await callback.message.edit_text(
            "🌿 Выберите ингредиент:",
            reply_markup=keyboard
        )
        await state.set_state(HopperFillStates.select_ingredient)

@router.callback_query(
    HopperFillStates.select_ingredient,
    F.data.startswith("ingredient:")
)
async def ingredient_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора ингредиента"""
    ingredient_id = int(callback.data.split(":")[1])
    await state.update_data(ingredient_id=ingredient_id)
    
    await callback.message.edit_text(
        "📏 Введите количество ингредиента ДО заполнения (кг):\n"
        "Например: 2.5"
    )
    await state.set_state(HopperFillStates.enter_quantity_before)

@router.message(HopperFillStates.enter_quantity_before)
async def quantity_before_entered(message: Message, state: FSMContext):
    """Обработка ввода количества до заполнения"""
    try:
        quantity = Decimal(message.text.replace(',', '.'))
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        
        await state.update_data(quantity_before=quantity)
        
        await message.answer(
            "📸 Отправьте фото бункера ДО заполнения:"
        )
        await state.set_state(HopperFillStates.photo_before)
        
    except (ValueError, TypeError):
        await message.answer(
            "❌ Неверный формат числа. Введите число, например: 2.5"
        )

@router.message(HopperFillStates.photo_before, F.photo)
async def photo_before_received(message: Message, state: FSMContext):
    """Обработка фото до заполнения"""
    # Получаем фото максимального размера
    photo = message.photo[-1]
    
    # Скачиваем фото
    photo_file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(photo_file.file_path)
    
    # Сохраняем фото
    photo_path = await file_service.save_photo(
        photo_data.read(),
        prefix="hopper_before"
    )
    
    data = await state.get_data()
    photos_before = data.get('photos_before', [])
    photos_before.append(photo_path)
    await state.update_data(photos_before=photos_before)
    
    await message.answer(
        "✅ Фото сохранено.\n\n"
        "📏 Введите количество добавленного ингредиента (кг):"
    )
    await state.set_state(HopperFillStates.enter_quantity_added)

@router.message(HopperFillStates.enter_quantity_added)
async def quantity_added_entered(message: Message, state: FSMContext):
    """Обработка ввода добавленного количества"""
    try:
        quantity = Decimal(message.text.replace(',', '.'))
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        
        await state.update_data(quantity_added=quantity)
        
        # Вычисляем количество после
        data = await state.get_data()
        quantity_after = data['quantity_before'] + quantity
        await state.update_data(quantity_after=quantity_after)
        
        await message.answer(
            f"📊 Рассчитано количество ПОСЛЕ заполнения: {quantity_after:.2f} кг\n\n"
            "📸 Отправьте фото бункера ПОСЛЕ заполнения:"
        )
        await state.set_state(HopperFillStates.photo_after)
        
    except (ValueError, TypeError):
        await message.answer(
            "❌ Неверный формат числа. Введите число, например: 3.0"
        )

@router.message(HopperFillStates.photo_after, F.photo)
async def photo_after_received(message: Message, state: FSMContext):
    """Обработка фото после заполнения"""
    # Обрабатываем фото аналогично
    photo = message.photo[-1]
    photo_file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(photo_file.file_path)
    
    photo_path = await file_service.save_photo(
        photo_data.read(),
        prefix="hopper_after"
    )
    
    data = await state.get_data()
    photos_after = data.get('photos_after', [])
    photos_after.append(photo_path)
    await state.update_data(photos_after=photos_after)
    
    # Получаем список машин
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        machines = await asset_service.get_assets(asset_type=AssetType.MACHINE)
        
        if machines:
            keyboard = get_machines_keyboard(machines)
            await message.answer(
                "☕ Выберите машину, куда устанавливается бункер:",
                reply_markup=keyboard
            )
            await state.set_state(HopperFillStates.select_machine)
        else:
            # Если нет машин, пропускаем этот шаг
            await show_confirmation(message, state)

@router.callback_query(
    HopperFillStates.select_machine,
    F.data.startswith("machine:")
)
async def machine_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора машины"""
    machine_id = int(callback.data.split(":")[1])
    await state.update_data(machine_id=machine_id)
    
    await callback.message.edit_text(
        "📝 Добавьте комментарий (необязательно):",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(HopperFillStates.notes)

@router.message(HopperFillStates.notes)
async def notes_entered(message: Message, state: FSMContext):
    """Обработка ввода комментария"""
    await state.update_data(notes=message.text)
    await show_confirmation(message, state)

@router.callback_query(HopperFillStates.notes, F.data == "skip")
async def skip_notes(callback: CallbackQuery, state: FSMContext):
    """Пропуск комментария"""
    await show_confirmation(callback.message, state)

async def show_confirmation(message: Message, state: FSMContext):
    """Показ подтверждения операции"""
    data = await state.get_data()
    
    # Получаем информацию об объектах
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        hopper = await asset_service.get(data['hopper_id'])
        
        from db.models.ingredient import Ingredient
        ingredient = await db.get(Ingredient, data['ingredient_id'])
        
        machine = None
        if data.get('machine_id'):
            machine = await asset_service.get(data['machine_id'])
    
    # Формируем текст подтверждения
    text = f"""
📋 **Подтвердите операцию заполнения:**

📦 **Бункер:** {hopper.name} ({hopper.inventory_number})
🌿 **Ингредиент:** {ingredient.name}
📏 **Количество ДО:** {data['quantity_before']:.2f} кг
➕ **Добавлено:** {data['quantity_added']:.2f} кг
📊 **Количество ПОСЛЕ:** {data['quantity_after']:.2f} кг
☕ **Машина:** {machine.name if machine else 'Не указана'}
📸 **Фото:** {len(data.get('photos_before', []))} до, {len(data.get('photos_after', []))} после
📝 **Комментарий:** {data.get('notes', 'Нет')}

Всё верно?
"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(HopperFillStates.confirm)

@router.callback_query(
    HopperFillStates.confirm,
    F.data == "confirm:yes"
)
async def confirm_operation(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение операции"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        # Получаем пользователя
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(
                "❌ Ошибка: пользователь не найден в системе"
            )
            await state.clear()
            return
        
        # Объединяем все фото
        all_photos = data.get('photos_before', []) + data.get('photos_after', [])
        
        # Создаем операцию
        from api.schemas import HopperOperationCreate
        from db.models.operation import OperationType
        
        operation_data = HopperOperationCreate(
            hopper_id=data['hopper_id'],
            operation_type=OperationType.FILL,
            ingredient_id=data['ingredient_id'],
            quantity_before=data['quantity_before'],
            quantity_after=data['quantity_after'],
            machine_id=data.get('machine_id'),
            notes=data.get('notes'),
            photos=all_photos
        )
        
        operation_service = OperationService(db)
        try:
            operation = await operation_service.create_hopper_operation(
                operation_data,
                operator_id=user.id
            )
            
            await callback.message.edit_text(
                f"✅ Операция заполнения успешно сохранена!\n"
                f"ID операции: {operation.id}"
            )
            
        except Exception as e:
            await callback.message.edit_text(
                f"❌ Ошибка при сохранении: {str(e)}"
            )
    
    await state.clear()

@router.callback_query(
    HopperFillStates.confirm,
    F.data == "confirm:no"
)
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    """Отмена операции"""
    await callback.message.edit_text("❌ Операция отменена")
    await state.clear()

# Обработчик отмены на любом этапе
@router.callback_query(F.data == "cancel")
async def cancel_any_state(callback: CallbackQuery, state: FSMContext):
    """Отмена на любом этапе"""
    await callback.message.edit_text("❌ Операция отменена")
    await state.clear()