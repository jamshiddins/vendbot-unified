import pandas as pd
import csv
from datetime import datetime
from decimal import Decimal
from typing import List
from pathlib import Path
import logging

from ..models.audit_models import FiscalReceipt, PaymentMethod
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class FiscalReceiptLoader(BaseLoader):
    """Загрузчик фискальных чеков"""
    
    REQUIRED_COLUMNS = [
        'receipt_number', 'machine_id', 'datetime', 
        'amount', 'payment_method'
    ]
    
    def load(self) -> List[FiscalReceipt]:
        """Загрузка чеков из CSV файла"""
        logger.info(f"Loading fiscal receipts from {self.filepath}")
        
        try:
            receipts = []
            
            with open(self.filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.validate_headers(reader.fieldnames, self.REQUIRED_COLUMNS)
                
                for idx, row in enumerate(reader):
                    try:
                        receipt = self._parse_receipt(row, idx)
                        receipts.append(receipt)
                    except Exception as e:
                        logger.error(f"Error parsing row {idx}: {e}")
                        continue
            
            logger.info(f"Loaded {len(receipts)} fiscal receipts")
            return receipts
            
        except Exception as e:
            logger.error(f"Error loading fiscal receipts: {e}")
            raise
    
    def _parse_receipt(self, row: dict, idx: int) -> FiscalReceipt:
        """Парсинг фискального чека"""
        # Парсим дату и время
        dt = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S')
        
        # Определяем метод оплаты
        payment_str = row['payment_method'].lower()
        if 'cash' in payment_str or 'налич' in payment_str:
            payment_method = PaymentMethod.CASH
        elif 'card' in payment_str or 'карт' in payment_str:
            payment_method = PaymentMethod.CARD
        else:
            payment_method = PaymentMethod.UNKNOWN
        
        return FiscalReceipt(
            receipt_number=row['receipt_number'],
            machine_id=str(row['machine_id']),
            datetime=dt,
            amount=Decimal(row['amount']),
            payment_method=payment_method,
            items=self._parse_items(row.get('items', '')),
            raw_data=row
        )
    
    def _parse_items(self, items_str: str) -> List[Dict[str, Any]]:
        """Парсинг позиций чека"""
        if not items_str:
            return []
        
        items = []
        # Предполагаем формат: "Product1:150;Product2:200"
        for item in items_str.split(';'):
            if ':' in item:
                name, amount = item.split(':', 1)
                items.append({
                    'name': name.strip(),
                    'amount': Decimal(amount.strip())
                })
        
        return items