# backend/db/models/unified.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
import enum

class AssetType(enum.Enum):
    MACHINE = "machine"
    HOPPER = "hopper"
    GRINDER = "grinder"
    
class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(AssetType), nullable=False)
    inventory_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    serial_number = Column(String(100))
    location = Column(String(200))
    status = Column(String(50), default='active')
    metadata = Column(JSON, default={})
    
class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    unit = Column(String(20))
    current_stock = Column(Numeric(10, 3), default=0)
    min_stock = Column(Numeric(10, 3), default=0)
    cost = Column(Numeric(10, 2))

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2))
    ingredients = relationship("RecipeIngredient", back_populates="recipe")

class HopperOperation(Base):
    __tablename__ = 'hopper_operations'
    
    id = Column(Integer, primary_key=True)
    hopper_id = Column(Integer, ForeignKey('assets.id'))
    operation_type = Column(String(50))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    quantity_before = Column(Numeric(10, 3))
    quantity_after = Column(Numeric(10, 3))
    operator_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, server_default=func.now())
    photos = Column(JSON, default=[])
    
    # Важно для синхронизации между каналами
    sync_status = Column(JSON, default={'telegram': False, 'web': False, 'mobile': False})