from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from datetime import datetime

from db.database import AsyncSessionLocal
from db.models.user import UserRole
from core.services.user_service import UserService
from core.services.file_service import file_service
from bot.states import WarehouseReceivingStates
from bot.keyboards.inline import get_ingredients_keyboard, get_confirm_keyboard
from bot.filters import RoleFilter
from api.websocket import ws_manager

router = Router(name="warehouse_receiving")

@router.message(F.text == "📥 Приемка", RoleFilter(UserRole.WAREHOUSE))
async def start_receiving(message: Message, state: FSMContext):
    """Начало процесса приемки товара"""
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        # Получаем список ингредиентов
        from sqlalchemy import select
        from db.models.ingredient import Ingredient
        
        result = await db.execute(select(Ingredient).order_by(Ingredient.name))
        ingredients = result.scalars().all()
        
        if not ingredients:
            await message.answer("❌ Нет ингредиентов в системе.")
            return
        
        keyboard = get_ingredients_keyboard(ingredients)
        await message.answer(
            "📦 Выберите ингредиент для приемки:",
            reply_markup=keyboard
        )
        await state.set_state(WarehouseReceivingStates.select_ingredient)

@router.callback_query(
    WarehouseReceivingStates.select_ingredient,
    F.data.startswith("ingredient:")
)
async def ingredient_selected_for_receiving(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора ингредиента"""
    ingredient_id = int(callback.data.split(":")[1])
    
    # Получаем информацию об ингредиенте
    async with AsyncSessionLocal() as db:
        from db.models.ingredient import Ingredient
        ingredient = await db.get(Ingredient, ingredient_id)
        
        await state.update_data(
            ingredient_id=ingredient_id,
            ingredient_name=ingredient.name,
            current_stock=float(ingredient.current_stock)
        )
    
    await callback.message.edit_text(
        f"📦 Приемка: {ingredient.name}\n"
        f"📊 Текущий остаток: {ingredient.current_stock} {ingredient.unit}\n\n"
        f"Введите количество принимаемого товара ({ingredient.unit}):"
    )
    await state.set_state(WarehouseReceivingStates.enter_quantity)

@router.message(WarehouseReceivingStates.enter_quantity)
async def quantity_entered(message: Message, state: FSMContext):
    """Обработка ввода количества"""
    try:
        quantity = Decimal(message.text.replace(',', '.'))
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
        
        await state.update_data(quantity=quantity)
        
        await message.answer(
            "📄 Введите номер накладной или счета-фактуры:"
        )
        await state.set_state(WarehouseReceivingStates.enter_invoice_number)
        
    except (ValueError, TypeError):
        await message.answer(
            "❌ Неверный формат числа. Введите положительное число."
        )

@router.message(WarehouseReceivingStates.enter_invoice_number)
async def invoice_entered(message: Message, state: FSMContext):
    """Обработка ввода номера накладной"""
    await state.update_data(invoice_number=message.text.strip())
    
    await message.answer(
        "📸 Отправьте фото коробок/упаковок принимаемого товара:"
    )
    await state.set_state(WarehouseReceivingStates.photo_boxes)

@router.message(WarehouseReceivingStates.photo_boxes, F.photo)
async def photo_received(message: Message, state: FSMContext):
    """Обработка фото"""
    photo = message.photo[-1]
    photo_file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(photo_file.file_path)
    
    photo_path = await file_service.save_photo(
        photo_data.read(),
        prefix="receiving"
    )
    
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(photo_path)
    await state.update_data(photos=photos)
    
    # Показываем подтверждение
    text = f"""
📋 **Подтвердите приемку товара:**

📦 **Товар:** {data['ingredient_name']}
📊 **Текущий остаток:** {data['current_stock']:.2f}
➕ **Принимается:** {data['quantity']:.2f}
📈 **Новый остаток:** {data['current_stock'] + float(data['quantity']):.2f}
📄 **Накладная:** {data['invoice_number']}
📸 **Фото:** {len(photos)} шт.

Всё верно?
"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(WarehouseReceivingStates.confirm)

@router.callback_query(
    WarehouseReceivingStates.confirm,
    F.data == "confirm:yes"
)
async def confirm_receiving(callback: CallbackQuery, state: FSMContext):
    """Подтверждение приемки"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        # Получаем пользователя
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram(callback.from_user.id)
        
        # Обновляем остатки
        from db.models.ingredient import Ingredient
        ingredient = await db.get(Ingredient, data['ingredient_id'])
        ingredient.current_stock += data['quantity']
        
        # Создаем запись о приемке
        from db.models.inventory import InventoryTransaction, TransactionType
        
        transaction = InventoryTransaction(
            ingredient_id=data['ingredient_id'],
            transaction_type=TransactionType.RECEIVING,
            quantity=data['quantity'],
            user_id=user.id,
            invoice_number=data['invoice_number'],
            photos=data.get('photos', []),
            notes=f"Приемка через Telegram"
        )
        
        db.add(transaction)
        await db.commit()
        
        # Отправляем через WebSocket
        await ws_manager.broadcast_inventory_update({
            'ingredient_id': data['ingredient_id'],
            'new_stock': float(ingredient.current_stock),
            'transaction_type': 'receiving',
            'quantity': float(data['quantity'])
        })
        
        await callback.message.edit_text(
            f"✅ Приемка успешно оформлена!\n\n"
            f"📦 {ingredient.name}\n"
            f"📊 Новый остаток: {ingredient.current_stock:.2f} {ingredient.unit}"
        )
    
    await state.clear()