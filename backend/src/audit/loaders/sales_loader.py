import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List
from pathlib import Path
import logging

from ..models.audit_models import SaleRecord, PaymentMethod
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class SalesLoader(BaseLoader):
    """Загрузчик данных о продажах"""
    
    REQUIRED_COLUMNS = [
        'machine_id', 'datetime', 'product_code', 
        'product_name', 'amount', 'payment_method'
    ]
    
    def load(self) -> List[SaleRecord]:
        """Загрузка продаж из Excel файла"""
        logger.info(f"Loading sales from {self.filepath}")
        
        try:
            df = pd.read_excel(self.filepath)
            self.validate_headers(df.columns.tolist(), self.REQUIRED_COLUMNS)
            
            sales = []
            for idx, row in df.iterrows():
                try:
                    sale = self._parse_sale_record(row, idx)
                    sales.append(sale)
                except Exception as e:
                    logger.error(f"Error parsing row {idx}: {e}")
                    continue
            
            logger.info(f"Loaded {len(sales)} sales records")
            return sales
            
        except Exception as e:
            logger.error(f"Error loading sales: {e}")
            raise
    
    def _parse_sale_record(self, row: pd.Series, idx: int) -> SaleRecord:
        """Парсинг записи о продаже"""
        # Определяем метод оплаты
        payment_str = str(row['payment_method']).lower()
        payment_method = self._map_payment_method(payment_str)
        
        # Парсим дату и время
        if isinstance(row['datetime'], str):
            dt = pd.to_datetime(row['datetime'])
        else:
            dt = row['datetime']
        
        return SaleRecord(
            id=f"SALE_{idx}_{row['machine_id']}_{dt.timestamp()}",
            machine_id=str(row['machine_id']),
            datetime=dt.to_pydatetime(),
            product_code=str(row['product_code']),
            product_name=str(row['product_name']),
            amount=Decimal(str(row['amount'])),
            payment_method=payment_method,
            quantity=int(row.get('quantity', 1)),
            raw_data=row.to_dict()
        )
    
    def _map_payment_method(self, payment_str: str) -> PaymentMethod:
        """Маппинг строки на enum метода оплаты"""
        mapping = {
            'cash': PaymentMethod.CASH,
            'наличные': PaymentMethod.CASH,
            'card': PaymentMethod.CARD,
            'карта': PaymentMethod.CARD,
            'click': PaymentMethod.QR_CLICK,
            'payme': PaymentMethod.QR_PAYME,
            'uzum': PaymentMethod.QR_UZUM,
            'vip': PaymentMethod.VIP,
            'test': PaymentMethod.TEST,
            'тест': PaymentMethod.TEST
        }
        
        return mapping.get(payment_str, PaymentMethod.UNKNOWN)