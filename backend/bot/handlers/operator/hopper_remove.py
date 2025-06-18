from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.database import AsyncSessionLocal
from db.models.asset import Asset, AssetType
from db.models.user import UserRole
from db.models.operation import HopperOperation, OperationType
from core.services.operation_service import OperationService
from core.services.user_service import UserService
from core.services.file_service import file_service
from bot.states import HopperRemoveStates
from bot.keyboards.inline import get_confirm_keyboard
from bot.filters import RoleFilter
from api.websocket import ws_manager

router = Router(name="hopper_remove")

@router.message(F.text == "📦 Снять бункер", RoleFilter(UserRole.OPERATOR))
async def start_hopper_remove(message: Message, state: FSMContext):
    """Начало процесса снятия бункера"""
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        # Получаем установленные бункера
        query = select(Asset).join(
            HopperOperation,
            and_(
                HopperOperation.hopper_id == Asset.id,
                HopperOperation.operation_type == OperationType.INSTALL
            )
        ).where(
            Asset.type == AssetType.HOPPER
        ).distinct()
        
        result = await db.execute(query)
        installed_hoppers = result.scalars().all()
        
        if not installed_hoppers:
            await message.answer("❌ Нет установленных бункеров для снятия.")
            return
        
        from bot.keyboards.inline import get_hoppers_keyboard
        keyboard = get_hoppers_keyboard(installed_hoppers)
        await message.answer(
            "📦 Выберите бункер для снятия:",
            reply_markup=keyboard
        )
        await state.set_state(HopperRemoveStates.select_hopper)

@router.callback_query(
    HopperRemoveStates.select_hopper,
    F.data.startswith("hopper:")
)
async def hopper_selected_for_remove(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора бункера для снятия"""
    hopper_id = int(callback.data.split(":")[1])
    await state.update_data(hopper_id=hopper_id)
    
    await callback.message.edit_text(
        "📸 Отправьте фото бункера перед снятием:"
    )
    await state.set_state(HopperRemoveStates.photo_before_remove)

@router.message(HopperRemoveStates.photo_before_remove, F.photo)
async def photo_before_remove_received(message: Message, state: FSMContext):
    """Обработка фото перед снятием"""
    # Обрабатываем фото
    photo = message.photo[-1]
    photo_file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(photo_file.file_path)
    
    photo_path = await file_service.save_photo(
        photo_data.read(),
        prefix="hopper_remove"
    )
    
    await state.update_data(photo=photo_path)
    
    # Показываем подтверждение
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        from core.services.asset_service import AssetService
        asset_service = AssetService(db)
        hopper = await asset_service.get(data['hopper_id'])
    
    text = f"""
📋 **Подтвердите снятие бункера:**

📦 **Бункер:** {hopper.name} ({hopper.inventory_number})
📸 **Фото:** Загружено

Подтверждаете снятие?
"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(HopperRemoveStates.confirm)

@router.callback_query(
    HopperRemoveStates.confirm,
    F.data == "confirm:yes"
)
async def confirm_remove(callback: CallbackQuery, state: FSMContext):
    """Подтверждение снятия"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        # Получаем пользователя
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            await state.clear()
            return
        
        # Создаем операцию снятия
        from api.schemas import HopperOperationCreate
        
        operation_data = HopperOperationCreate(
            hopper_id=data['hopper_id'],
            operation_type=OperationType.REMOVE,
            photos=[data['photo']]
        )
        
        operation_service = OperationService(db)
        try:
            operation = await operation_service.create_hopper_operation(
                operation_data,
                operator_id=user.id
            )
            
            # Отправляем через WebSocket
            await ws_manager.broadcast_operation(
                operation.dict(),
                source_channel="telegram"
            )
            
            await callback.message.edit_text(
                f"✅ Бункер успешно снят!\n"
                f"ID операции: {operation.id}"
            )
            
        except Exception as e:
            await callback.message.edit_text(
                f"❌ Ошибка при сохранении: {str(e)}"
            )
    
    await state.clear()