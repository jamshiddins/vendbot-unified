from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class OperationType(str, enum.Enum):
    FILL = "fill"
    INSTALL = "install"
    REMOVE = "remove"
    CLEAN = "clean"
    CHECK = "check"

class HopperOperation(Base, TimestampMixin):
    __tablename__ = "hopper_operations"
    
    id = Column(Integer, primary_key=True)
    hopper_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    operation_type = Column(Enum(OperationType), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    quantity_before = Column(Numeric(10, 3))
    quantity_after = Column(Numeric(10, 3))
    quantity_added = Column(Numeric(10, 3))
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("assets.id"))
    photos = Column(JSON, default=list)
    notes = Column(String(500))
    sync_status = Column(JSON, default=lambda: {"telegram": False, "web": False, "mobile": False})
    
    # Relationships
    hopper = relationship("Asset", back_populates="hopper_operations", foreign_keys=[hopper_id])
    machine = relationship("Asset", foreign_keys=[machine_id])
    ingredient = relationship("Ingredient", back_populates="operations")
    operator = relationship("User", back_populates="operations")
    
    def __repr__(self):
        return f"<HopperOperation {self.id} - {self.operation_type.value}>"