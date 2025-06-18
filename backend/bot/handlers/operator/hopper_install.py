from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import AsyncSessionLocal
from db.models.asset import AssetType
from db.models.user import UserRole
from db.models.operation import OperationType
from core.services.asset_service import AssetService
from core.services.operation_service import OperationService
from core.services.user_service import UserService
from core.services.file_service import file_service
from bot.states import HopperInstallStates
from bot.keyboards.inline import (
    get_hoppers_keyboard,
    get_machines_keyboard,
    get_confirm_keyboard
)
from bot.filters import RoleFilter
from api.websocket import ws_manager

router = Router(name="hopper_install")

@router.message(F.text == "📦 Установить бункер", RoleFilter(UserRole.OPERATOR))
async def start_hopper_install(message: Message, state: FSMContext):
    """Начало процесса установки бункера"""
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        hoppers = await asset_service.get_available_hoppers()
        
        if not hoppers:
            await message.answer("❌ Нет доступных бункеров для установки.")
            return
        
        keyboard = get_hoppers_keyboard(hoppers)
        await message.answer(
            "📦 Выберите бункер для установки:",
            reply_markup=keyboard
        )
        await state.set_state(HopperInstallStates.select_hopper)

@router.callback_query(
    HopperInstallStates.select_hopper,
    F.data.startswith("hopper:")
)
async def hopper_selected_for_install(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора бункера"""
    hopper_id = int(callback.data.split(":")[1])
    await state.update_data(hopper_id=hopper_id)
    
    # Получаем список машин
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        machines = await asset_service.get_assets(asset_type=AssetType.MACHINE)
        
        if not machines:
            await callback.message.edit_text("❌ Нет доступных машин.")
            await state.clear()
            return
        
        keyboard = get_machines_keyboard(machines)
        await callback.message.edit_text(
            "☕ Выберите машину для установки бункера:",
            reply_markup=keyboard
        )
        await state.set_state(HopperInstallStates.select_machine)

@router.callback_query(
    HopperInstallStates.select_machine,
    F.data.startswith("machine:")
)
async def machine_selected_for_install(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора машины"""
    machine_id = int(callback.data.split(":")[1])
    await state.update_data(machine_id=machine_id)
    
    await callback.message.edit_text(
        "📸 Отправьте фото установленного бункера:"
    )
    await state.set_state(HopperInstallStates.photo_installation)

@router.message(HopperInstallStates.photo_installation, F.photo)
async def photo_installation_received(message: Message, state: FSMContext):
    """Обработка фото установки"""
    # Обрабатываем фото
    photo = message.photo[-1]
    photo_file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(photo_file.file_path)
    
    photo_path = await file_service.save_photo(
        photo_data.read(),
        prefix="hopper_install"
    )
    
    await state.update_data(photo=photo_path)
    
    # Показываем подтверждение
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        asset_service = AssetService(db)
        hopper = await asset_service.get(data['hopper_id'])
        machine = await asset_service.get(data['machine_id'])
    
    text = f"""
📋 **Подтвердите установку бункера:**

📦 **Бункер:** {hopper.name} ({hopper.inventory_number})
☕ **Машина:** {machine.name} - {machine.location or 'Не указано'}
📸 **Фото:** Загружено

Всё верно?
"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(HopperInstallStates.confirm)

@router.callback_query(
    HopperInstallStates.confirm,
    F.data == "confirm:yes"
)
async def confirm_install(callback: CallbackQuery, state: FSMContext):
    """Подтверждение установки"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as db:
        # Получаем пользователя
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            await state.clear()
            return
        
        # Создаем операцию
        from api.schemas import HopperOperationCreate
        
        operation_data = HopperOperationCreate(
            hopper_id=data['hopper_id'],
            operation_type=OperationType.INSTALL,
            machine_id=data['machine_id'],
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
                f"✅ Бункер успешно установлен!\n"
                f"ID операции: {operation.id}"
            )
            
        except Exception as e:
            await callback.message.edit_text(
                f"❌ Ошибка при сохранении: {str(e)}"
            )
    
    await state.clear()