from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    QR_CLICK = "qr_click"
    QR_PAYME = "qr_payme"
    QR_UZUM = "qr_uzum"
    VIP = "vip"
    TEST = "test"
    UNKNOWN = "unknown"

class DiscrepancyType(Enum):
    MISSING_RECEIPT = "missing_receipt"
    MISSING_TRANSACTION = "missing_transaction"
    DUPLICATE_SALE = "duplicate_sale"
    AMOUNT_MISMATCH = "amount_mismatch"
    TIME_MISMATCH = "time_mismatch"
    TEST_SALE = "test_sale"
    EXCESS_CONSUMPTION = "excess_consumption"
    UNKNOWN_PAYMENT = "unknown_payment"

@dataclass
class SaleRecord:
    """Запись о продаже из системы вендинга"""
    id: str
    machine_id: str
    datetime: datetime
    product_code: str
    product_name: str
    amount: Decimal
    payment_method: PaymentMethod
    quantity: int = 1
    raw_data: Dict[str, Any] = None
    
    def __hash__(self):
        return hash((self.machine_id, self.datetime, self.amount))

@dataclass
class FiscalReceipt:
    """Фискальный чек из ККМ"""
    receipt_number: str
    machine_id: str
    datetime: datetime
    amount: Decimal
    payment_method: PaymentMethod  # cash or card
    items: List[Dict[str, Any]] = None
    raw_data: Dict[str, Any] = None
    
    def __hash__(self):
        return hash((self.machine_id, self.datetime, self.amount))

@dataclass
class QRTransaction:
    """Транзакция через QR-код"""
    transaction_id: str
    service: str  # click, payme, uzum
    datetime: datetime
    amount: Decimal
    machine_id: Optional[str] = None
    status: str = "success"
    raw_data: Dict[str, Any] = None
    
    def __hash__(self):
        return hash((self.service, self.transaction_id))

@dataclass
class InventoryMovement:
    """Движение ингредиентов"""
    datetime: datetime
    machine_id: str
    ingredient_code: str
    ingredient_name: str
    quantity: Decimal
    unit: str
    movement_type: str  # refill, consumption, adjustment
    operator_id: Optional[str] = None

@dataclass
class RecipeIngredient:
    """Ингредиент в рецепте"""
    ingredient_code: str
    ingredient_name: str
    quantity: Decimal
    unit: str

@dataclass
class Recipe:
    """Рецепт напитка"""
    product_code: str
    product_name: str
    ingredients: List[RecipeIngredient]
    category: str = "coffee"

@dataclass
class Discrepancy:
    """Несоответствие при сверке"""
    type: DiscrepancyType
    machine_id: str
    datetime: datetime
    description: str
    sale_record: Optional[SaleRecord] = None
    receipt: Optional[FiscalReceipt] = None
    transaction: Optional[QRTransaction] = None
    amount_difference: Optional[Decimal] = None
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class ReconciliationResult:
    """Результат сверки"""
    period_start: datetime
    period_end: datetime
    total_sales: int
    total_receipts: int
    total_transactions: int
    matched_count: int
    discrepancies: List[Discrepancy]
    summary_by_machine: Dict[str, Dict[str, Any]]
    summary_by_payment: Dict[str, Dict[str, Any]]