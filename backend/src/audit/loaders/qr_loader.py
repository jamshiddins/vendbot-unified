import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List
from pathlib import Path
import logging

from ..models.audit_models import QRTransaction
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class QRTransactionLoader(BaseLoader):
    """Загрузчик QR транзакций"""
    
    # Маппинг колонок для разных платежных систем
    COLUMN_MAPPINGS = {
        'click': {
            'transaction_id': 'payment_id',
            'datetime': 'payment_date',
            'amount': 'amount',
            'status': 'status',
            'machine_id': 'merchant_trans_id'
        },
        'payme': {
            'transaction_id': 'transaction',
            'datetime': 'create_time',
            'amount': 'amount',
            'status': 'state',
            'machine_id': 'order_id'
        },
        'uzum': {
            'transaction_id': 'trans_id',
            'datetime': 'created_at',
            'amount': 'amount',
            'status': 'status',
            'machine_id': 'external_id'
        }
    }
    
    def __init__(self, filepath: Path, service: str):
        super().__init__(filepath)
        self.service = service.lower()
        if self.service not in self.COLUMN_MAPPINGS:
            raise ValueError(f"Unknown QR service: {service}")
    
    def load(self) -> List[QRTransaction]:
        """Загрузка QR транзакций"""
        logger.info(f"Loading {self.service} transactions from {self.filepath}")
        
        try:
            df = pd.read_excel(self.filepath)
            transactions = []
            
            mapping = self.COLUMN_MAPPINGS[self.service]
            
            for idx, row in df.iterrows():
                try:
                    transaction = self._parse_transaction(row, mapping, idx)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logger.error(f"Error parsing row {idx}: {e}")
                    continue
            
            logger.info(f"Loaded {len(transactions)} {self.service} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Error loading QR transactions: {e}")
            raise
    
    def _parse_transaction(self, row: pd.Series, mapping: dict, idx: int) -> QRTransaction:
        """Парсинг транзакции"""
        # Получаем значения по маппингу
        trans_id = str(row.get(mapping['transaction_id'], f"{self.service}_{idx}"))
        
        # Парсим дату
        dt_value = row.get(mapping['datetime'])
        if isinstance(dt_value, str):
            dt = pd.to_datetime(dt_value)
        else:
            dt = dt_value
        
        # Парсим сумму (для некоторых систем может быть в тийинах)
        amount = Decimal(str(row.get(mapping['amount'], 0)))
        if self.service in ['payme', 'click'] and amount > 10000:
            amount = amount / 100  # Конвертируем из тийинов в сумы
        
        # Извлекаем ID машины из merchant_trans_id или order_id
        machine_id = None
        if mapping.get('machine_id'):
            machine_id_raw = str(row.get(mapping['machine_id'], ''))
            # Пытаемся извлечь ID машины из строки
            machine_id = self._extract_machine_id(machine_id_raw)
        
        return QRTransaction(
            transaction_id=trans_id,
            service=self.service,
            datetime=dt.to_pydatetime() if hasattr(dt, 'to_pydatetime') else dt,
            amount=amount,
            machine_id=machine_id,
            status=str(row.get(mapping.get('status', 'status'), 'success')),
            raw_data=row.to_dict()
        )
    
    def _extract_machine_id(self, raw_id: str) -> Optional[str]:
        """Извлечение ID машины из строки"""
        # Примеры форматов:
        # "VM_001_2024-06-14_12345"
        # "machine-15-order-789"
        # "15"
        
        if not raw_id:
            return None
        
        # Пытаемся найти числовой ID
        import re
        
        # Паттерны для поиска ID машины
        patterns = [
            r'VM[_-]?(\d+)',
            r'machine[_-]?(\d+)',
            r'^(\d+)$',
            r'_(\d+)_'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_id, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return raw_id  # Возвращаем как есть, если не смогли распарсить