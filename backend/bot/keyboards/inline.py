from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional
from db.models.asset import Asset, AssetType
from db.models.ingredient import Ingredient

def get_hoppers_keyboard(hoppers: List[Asset]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора бункера"""
    builder = InlineKeyboardBuilder()
    
    for hopper in hoppers:
        builder.button(
            text=f"📦 {hopper.name} ({hopper.inventory_number})",
            callback_data=f"hopper:{hopper.id}"
        )
    
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(1)
    
    return builder.as_markup()

def get_ingredients_keyboard(ingredients: List[Ingredient]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора ингредиента"""
    builder = InlineKeyboardBuilder()
    
    for ingredient in ingredients:
        text = f"{ingredient.name} ({ingredient.current_stock:.1f} {ingredient.unit})"
        builder.button(
            text=text,
            callback_data=f"ingredient:{ingredient.id}"
        )
    
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(1)
    
    return builder.as_markup()

def get_machines_keyboard(machines: List[Asset]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора машины"""
    builder = InlineKeyboardBuilder()
    
    for machine in machines:
        builder.button(
            text=f"☕ {machine.name} - {machine.location or 'Не указано'}",
            callback_data=f"machine:{machine.id}"
        )
    
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(1)
    
    return builder.as_markup()

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm:yes")
    builder.button(text="❌ Отмена", callback_data="confirm:no")
    builder.adjust(2)
    
    return builder.as_markup()

def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска шага"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭️ Пропустить", callback_data="skip")
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(2)
    
    return builder.as_markup()