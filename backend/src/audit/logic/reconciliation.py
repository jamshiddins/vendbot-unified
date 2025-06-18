from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import logging

from ..models.audit_models import (
    SaleRecord, FiscalReceipt, QRTransaction,
    Discrepancy, DiscrepancyType, PaymentMethod,
    ReconciliationResult
)

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """Движок сверки данных"""
    
    def __init__(self, 
                 time_tolerance_seconds: int = 30,
                 amount_tolerance: Decimal = Decimal('1')):
        self.time_tolerance = timedelta(seconds=time_tolerance_seconds)
        self.amount_tolerance = amount_tolerance
    
    def reconcile_all(self,
                     sales: List[SaleRecord],
                     receipts: List[FiscalReceipt],
                     qr_transactions: List[QRTransaction],
                     period_start: datetime,
                     period_end: datetime) -> ReconciliationResult:
        """Полная сверка всех данных"""
        logger.info(f"Starting reconciliation for period {period_start} to {period_end}")
        
        discrepancies = []
        
        # 1. Сверяем продажи с чеками и транзакциями
        sales_discrepancies = self._reconcile_sales(sales, receipts, qr_transactions)
        discrepancies.extend(sales_discrepancies)
        
        # 2. Ищем чеки без продаж
        orphan_receipts = self._find_orphan_receipts(sales, receipts)
        discrepancies.extend(orphan_receipts)
        
        # 3. Ищем транзакции без продаж
        orphan_transactions = self._find_orphan_transactions(sales, qr_transactions)
        discrepancies.extend(orphan_transactions)
        
        # 4. Ищем дубликаты
        duplicates = self._find_duplicates(sales)
        discrepancies.extend(duplicates)
        
        # 5. Формируем сводку
        result = self._create_summary(
            sales, receipts, qr_transactions, 
            discrepancies, period_start, period_end
        )
        
        logger.info(f"Reconciliation completed. Found {len(discrepancies)} discrepancies")
        
        return result
    
    def _reconcile_sales(self, 
                        sales: List[SaleRecord],
                        receipts: List[FiscalReceipt],
                        qr_transactions: List[QRTransaction]) -> List[Discrepancy]:
        """Сверка каждой продажи с чеками/транзакциями"""
        discrepancies = []
        
        # Индексируем чеки и транзакции для быстрого поиска
        receipts_by_machine = self._index_by_machine_and_time(receipts)
        qr_by_time = self._index_qr_by_time(qr_transactions)
        
        for sale in sales:
            # Пропускаем тестовые продажи
            if sale.payment_method == PaymentMethod.TEST:
                discrepancies.append(Discrepancy(
                    type=DiscrepancyType.TEST_SALE,
                    machine_id=sale.machine_id,
                    datetime=sale.datetime,
                    description=f"Test sale: {sale.product_name} for {sale.amount}",
                    sale_record=sale,
                    severity="low"
                ))
                continue
            
            # Ищем соответствие в зависимости от метода оплаты
            if sale.payment_method in [PaymentMethod.CASH, PaymentMethod.CARD]:
                match = self._find_receipt_match(sale, receipts_by_machine)
                if not match:
                    discrepancies.append(Discrepancy(
                        type=DiscrepancyType.MISSING_RECEIPT,
                        machine_id=sale.machine_id,
                        datetime=sale.datetime,
                        description=f"No fiscal receipt found for {sale.payment_method.value} sale",
                        sale_record=sale,
                        severity="high"
                    ))
            
            elif sale.payment_method in [PaymentMethod.QR_CLICK, PaymentMethod.QR_PAYME, PaymentMethod.QR_UZUM]:
                match = self._find_qr_match(sale, qr_by_time)
                if not match:
                    discrepancies.append(Discrepancy(
                        type=DiscrepancyType.MISSING_TRANSACTION,
                        machine_id=sale.machine_id,
                        datetime=sale.datetime,
                        description=f"No QR transaction found for {sale.payment_method.value} sale",
                        sale_record=sale,
                        severity="high"
                    ))
            
            elif sale.payment_method == PaymentMethod.VIP:
                # VIP продажи могут не иметь чеков
                logger.info(f"VIP sale: {sale.id}")
            
            else:
                discrepancies.append(Discrepancy(
                    type=DiscrepancyType.UNKNOWN_PAYMENT,
                    machine_id=sale.machine_id,
                    datetime=sale.datetime,
                    description=f"Unknown payment method: {sale.payment_method.value}",
                    sale_record=sale,
                    severity="medium"
                ))
        
        return discrepancies
    
    def _find_receipt_match(self, 
                           sale: SaleRecord, 
                           receipts_index: Dict) -> Optional[FiscalReceipt]:
        """Поиск соответствующего чека для продажи"""
        machine_receipts = receipts_index.get(sale.machine_id, {})
        
        # Ищем в пределах временного окна
        min_time = sale.datetime - self.time_tolerance
        max_time = sale.datetime + self.time_tolerance
        
        for dt in sorted(machine_receipts.keys()):
            if min_time <= dt <= max_time:
                for receipt in machine_receipts[dt]:
                    # Проверяем сумму
                    if abs(receipt.amount - sale.amount) <= self.amount_tolerance:
                        # Проверяем метод оплаты
                        if self._payment_methods_match(sale.payment_method, receipt.payment_method):
                            return receipt
        
        return None
    
    def _find_qr_match(self,
                      sale: SaleRecord,
                      qr_index: Dict) -> Optional[QRTransaction]:
        """Поиск соответствующей QR транзакции"""
        # Определяем сервис по методу оплаты
        service_map = {
            PaymentMethod.QR_CLICK: 'click',
            PaymentMethod.QR_PAYME: 'payme',
            PaymentMethod.QR_UZUM: 'uzum'
        }
        
        service = service_map.get(sale.payment_method)
        if not service:
            return None
        
        # Ищем в пределах временного окна
        min_time = sale.datetime - self.time_tolerance
        max_time = sale.datetime + self.time_tolerance
        
        for dt in sorted(qr_index.keys()):
            if min_time <= dt <= max_time:
                for transaction in qr_index[dt]:
                    if transaction.service == service:
                        # Проверяем сумму
                        if abs(transaction.amount - sale.amount) <= self.amount_tolerance:
                            # Проверяем машину если есть
                            if not transaction.machine_id or transaction.machine_id == sale.machine_id:
                                return transaction
        
        return None
    
    def _payment_methods_match(self, sale_method: PaymentMethod, receipt_method: PaymentMethod) -> bool:
        """Проверка соответствия методов оплаты"""
        # Прямое совпадение
        if sale_method == receipt_method:
            return True
        
        # Дополнительные правила маппинга
        # Например, если в продаже "card", а в чеке "unknown", но это не наличные
        if sale_method == PaymentMethod.CARD and receipt_method == PaymentMethod.UNKNOWN:
            return True
        
        return False
    
    def _find_orphan_receipts(self,
                             sales: List[SaleRecord],
                             receipts: List[FiscalReceipt]) -> List[Discrepancy]:
        """Поиск чеков без соответствующих продаж"""
        discrepancies = []
        sales_index = self._index_sales_by_machine_and_time(sales)
        
        for receipt in receipts:
            if not self._find_sale_for_receipt(receipt, sales_index):
                discrepancies.append(Discrepancy(
                    type=DiscrepancyType.MISSING_RECEIPT,
                    machine_id=receipt.machine_id,
                    datetime=receipt.datetime,
                    description=f"Fiscal receipt without sale: {receipt.receipt_number}",
                    receipt=receipt,
                    severity="medium"
                ))
        
        return discrepancies
    
    def _find_orphan_transactions(self,
                                 sales: List[SaleRecord],
                                 transactions: List[QRTransaction]) -> List[Discrepancy]:
        """Поиск транзакций без соответствующих продаж"""
        discrepancies = []
        sales_by_amount = self._index_sales_by_amount_and_time(sales)
        
        for transaction in transactions:
            if not self._find_sale_for_transaction(transaction, sales_by_amount):
                discrepancies.append(Discrepancy(
                    type=DiscrepancyType.MISSING_TRANSACTION,
                    machine_id=transaction.machine_id or "UNKNOWN",
                    datetime=transaction.datetime,
                    description=f"{transaction.service} transaction without sale: {transaction.transaction_id}",
                    transaction=transaction,
                    severity="medium"
                ))
        
        return discrepancies
    
    def _find_duplicates(self, sales: List[SaleRecord]) -> List[Discrepancy]:
        """Поиск дублирующих продаж"""
        discrepancies = []
        seen = set()
        
        for sale in sales:
            # Ключ для определения дубликата
            key = (sale.machine_id, sale.datetime, sale.amount, sale.product_code)
            
            if key in seen:
                discrepancies.append(Discrepancy(
                    type=DiscrepancyType.DUPLICATE_SALE,
                    machine_id=sale.machine_id,
                    datetime=sale.datetime,
                    description=f"Duplicate sale: {sale.product_name} for {sale.amount}",
                    sale_record=sale,
                    severity="high"
                ))
            else:
                seen.add(key)
        
        return discrepancies
    
    def _index_by_machine_and_time(self, 
                                   receipts: List[FiscalReceipt]) -> Dict[str, Dict[datetime, List[FiscalReceipt]]]:
        """Индексация чеков по машине и времени"""
        index = defaultdict(lambda: defaultdict(list))
        
        for receipt in receipts:
            index[receipt.machine_id][receipt.datetime].append(receipt)
        
        return dict(index)
    
    def _index_qr_by_time(self, 
                         transactions: List[QRTransaction]) -> Dict[datetime, List[QRTransaction]]:
        """Индексация QR транзакций по времени"""
        index = defaultdict(list)
        
        for transaction in transactions:
            index[transaction.datetime].append(transaction)
        
        return dict(index)
    
    def _index_sales_by_machine_and_time(self,
                                        sales: List[SaleRecord]) -> Dict[str, Dict[datetime, List[SaleRecord]]]:
        """Индексация продаж по машине и времени"""
        index = defaultdict(lambda: defaultdict(list))
        
        for sale in sales:
            index[sale.machine_id][sale.datetime].append(sale)
        
        return dict(index)
    
    def _index_sales_by_amount_and_time(self,
                                       sales: List[SaleRecord]) -> Dict[Decimal, Dict[datetime, List[SaleRecord]]]:
        """Индексация продаж по сумме и времени"""
        index = defaultdict(lambda: defaultdict(list))
        
        for sale in sales:
            index[sale.amount][sale.datetime].append(sale)
        
        return dict(index)
    
    def _find_sale_for_receipt(self,
                              receipt: FiscalReceipt,
                              sales_index: Dict) -> Optional[SaleRecord]:
        """Поиск продажи для чека"""
        machine_sales = sales_index.get(receipt.machine_id, {})
        
        min_time = receipt.datetime - self.time_tolerance
        max_time = receipt.datetime + self.time_tolerance
        
        for dt in sorted(machine_sales.keys()):
            if min_time <= dt <= max_time:
                for sale in machine_sales[dt]:
                    if abs(sale.amount - receipt.amount) <= self.amount_tolerance:
                        return sale
        
        return None
    
    def _find_sale_for_transaction(self,
                                  transaction: QRTransaction,
                                  sales_index: Dict) -> Optional[SaleRecord]:
        """Поиск продажи для транзакции"""
        amount_sales = sales_index.get(transaction.amount, {})
        
        min_time = transaction.datetime - self.time_tolerance
        max_time = transaction.datetime + self.time_tolerance
        
        for dt in sorted(amount_sales.keys()):
            if min_time <= dt <= max_time:
                for sale in amount_sales[dt]:
                    # Проверяем соответствие метода оплаты
                    expected_method = {
                        'click': PaymentMethod.QR_CLICK,
                        'payme': PaymentMethod.QR_PAYME,
                        'uzum': PaymentMethod.QR_UZUM
                    }.get(transaction.service)
                    
                    if sale.payment_method == expected_method:
                        # Проверяем машину если указана
                        if not transaction.machine_id or transaction.machine_id == sale.machine_id:
                            return sale
        
        return None
    
    def _create_summary(self,
                       sales: List[SaleRecord],
                       receipts: List[FiscalReceipt],
                       transactions: List[QRTransaction],
                       discrepancies: List[Discrepancy],
                       period_start: datetime,
                       period_end: datetime) -> ReconciliationResult:
        """Создание сводного отчета"""
        # Подсчет совпадений
        matched_count = len(sales) - len([d for d in discrepancies 
                                         if d.type in [DiscrepancyType.MISSING_RECEIPT, 
                                                      DiscrepancyType.MISSING_TRANSACTION]])
        
        # Сводка по машинам
        summary_by_machine = defaultdict(lambda: {
            'total_sales': 0,
            'total_amount': Decimal('0'),
            'discrepancies': 0,
            'payment_methods': defaultdict(int)
        })
        
        for sale in sales:
            summary_by_machine[sale.machine_id]['total_sales'] += 1
            summary_by_machine[sale.machine_id]['total_amount'] += sale.amount
            summary_by_machine[sale.machine_id]['payment_methods'][sale.payment_method.value] += 1
        
        for discrepancy in discrepancies:
            summary_by_machine[discrepancy.machine_id]['discrepancies'] += 1
        
        # Сводка по методам оплаты
        summary_by_payment = defaultdict(lambda: {
            'count': 0,
            'amount': Decimal('0'),
            'matched': 0,
            'unmatched': 0
        })
        
        for sale in sales:
            payment_key = sale.payment_method.value
            summary_by_payment[payment_key]['count'] += 1
            summary_by_payment[payment_key]['amount'] += sale.amount
            
            # Проверяем, есть ли несоответствие для этой продажи
            has_discrepancy = any(
                d.sale_record == sale and 
                d.type in [DiscrepancyType.MISSING_RECEIPT, DiscrepancyType.MISSING_TRANSACTION]
                for d in discrepancies
            )
            
            if has_discrepancy:
                summary_by_payment[payment_key]['unmatched'] += 1
            else:
                summary_by_payment[payment_key]['matched'] += 1
        
        return ReconciliationResult(
            period_start=period_start,
            period_end=period_end,
            total_sales=len(sales),
            total_receipts=len(receipts),
            total_transactions=len(transactions),
            matched_count=matched_count,
            discrepancies=discrepancies,
            summary_by_machine=dict(summary_by_machine),
            summary_by_payment=dict(summary_by_payment)
        )