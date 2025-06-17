from aiogram.fsm.state import StatesGroup, State

class HopperFillStates(StatesGroup):
    """Состояния для заполнения бункера"""
    select_hopper = State()
    scan_hopper = State()
    select_ingredient = State()
    enter_quantity_before = State()
    photo_before = State()
    enter_quantity_added = State()
    enter_quantity_after = State()
    photo_after = State()
    select_machine = State()
    notes = State()
    confirm = State()

class HopperInstallStates(StatesGroup):
    """Состояния для установки бункера"""
    select_hopper = State()
    select_machine = State()
    photo_installation = State()
    confirm = State()

class HopperRemoveStates(StatesGroup):
    """Состояния для снятия бункера"""
    select_hopper = State()
    photo_before_remove = State()
    confirm = State()