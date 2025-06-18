from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class TransactionType(str, enum.Enum):
    RECEIVING = "receiving"
    ISSUE = "issue"
    ADJUSTMENT = "adjustment"
    WRITE_OFF = "write_off"
    RETURN = "return"

class InventoryTransaction(Base, TimestampMixin):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)  # + приход, - расход
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    invoice_number = Column(String(100))
    photos = Column(JSON, default=list)
    notes = Column(String(500))
    
    # Relationships
    ingredient = relationship("Ingredient")
    user = relationship("User", foreign_keys=[user_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

class RoutePoint(Base, TimestampMixin):
    __tablename__ = "route_points"
    
    id = Column(Integer, primary_key=True)
    route_date = Column(DateTime, nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location_name = Column(String(200), nullable=False)
    location_address = Column(String(500))
    machines_count = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    arrival_time = Column(DateTime)
    departure_time = Column(DateTime)
    status = Column(String(50), default="pending")
    
    # Relationships
    driver = relationship("User")