from sqlalchemy import Column, Integer, String, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class AssetType(str, enum.Enum):
    MACHINE = "machine"
    HOPPER = "hopper"
    GRINDER = "grinder"

class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Asset(Base, TimestampMixin):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(AssetType), nullable=False)
    inventory_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    serial_number = Column(String(100))
    location = Column(String(200))
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    hopper_operations = relationship(
        "HopperOperation", 
        back_populates="hopper",
        foreign_keys="HopperOperation.hopper_id"
    )
    
    def __repr__(self):
        return f"<Asset {self.inventory_number} - {self.name}>"