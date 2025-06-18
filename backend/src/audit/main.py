#!/usr/bin/env python3
"""
VendBot Audit Module - Сверка отчетности вендинговых автоматов
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys

from .loaders import (
    SalesLoader, FiscalReceiptLoader, QRTransactionLoader,
    RecipeLoader
)
from .logic import ReconciliationEngine
from .reports import ExcelReporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audit.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AuditRunner:
    """Основной класс для запуска аудита"""
    
    def __init__(self, data_folder: Path, output_folder: Path):
        self.data_folder = data_folder
        self.output_folder = output_folder
        self.output_folder.mkdir(exist_ok=True)
    
    def run(self, period_start: datetime, period_end: datetime):
        """Запуск процесса аудита"""
        logger.info("=" * 80)
        logger.info(f"Starting VendBot Audit for period {period_start.date()} to {period_end.date()}")
        logger.info("=" * 80)
        
        try:
            # 1. Загрузка данных
            logger.info("Step 1: Loading data files...")
            data = self._load_all_data()
            
            # 2. Сверка
            logger.info("Step 2: Running reconciliation...")
            engine = ReconciliationEngine()
            result = engine.reconcile_all(
                sales=data['sales'],
                receipts=data['receipts'],
                qr_transactions=data['qr_transactions'],
                period_start=period_start,
                period_end=period_end
            )
            
            # 3. Генерация отчетов
            logger.info("Step 3: Generating reports...")
            self._generate_reports(result, period_start, period_end)
            
            # 4. Вывод сводки
            self._print_summary(result)
            
            logger.info("=" * 80)
            logger.info("Audit completed successfully!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Audit failed: {e}", exc_info=True)
            sys.exit(1)
    
    def _load_all_data(self) -> dict:
        """Загрузка всех необходимых файлов"""
        data = {
            'sales': [],
            'receipts': [],
            'qr_transactions': [],
            'recipes': {}
        }
        
        # Загрузка продаж
        sales_file = self.data_folder / 'sales_report.xlsx'
        if sales_file.exists():
            loader = SalesLoader(sales_file)
            data['sales'] = loader.load()
        else:
            logger.warning(f"Sales file not found: {sales_file}")
        
        # Загрузка чеков
        receipts_file = self.data_folder / 'kkm_receipts.csv'
        if receipts_file.exists():
            loader = FiscalReceiptLoader(receipts_file)
            data['receipts'] = loader.load()
        else:
            logger.warning(f"Receipts file not found: {receipts_file}")
        
        # Загрузка QR транзакций
        qr_services = ['click', 'payme', 'uzum']
        for service in qr_services:
            qr_file = self.data_folder / f'qr_{service}.xlsx'
            if qr_file.exists():
                loader = QRTransactionLoader(qr_file, service)
                data['qr_transactions'].extend(loader.load())
            else:
                logger.warning(f"QR file not found: {qr_file}")
        
        # Загрузка рецептов
        recipes_file = self.data_folder / 'recipes.json'
        if recipes_file.exists():
            loader = RecipeLoader(recipes_file)
            data['recipes'] = loader.load()
        else:
            logger.warning(f"Recipes file not found: {recipes_file}")
        
        return data
    
    def _generate_reports(self, result, period_start: datetime, period_end: datetime):
        """Генерация отчетов"""
        reporter = ExcelReporter()
        
        # Основной отчет
        report_name = f"audit_report_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.xlsx"
        report_path = self.output_folder / report_name
        
        reporter.generate_reconciliation_report(result, report_path)
        logger.info(f"Report saved to: {report_path}")
    
    def _print_summary(self, result):
        """Вывод сводки в консоль"""
        print("\n" + "=" * 60)
        print("СВОДКА АУДИТА")
        print("=" * 60)
        print(f"Период: {result.period_start.date()} - {result.period_end.date()}")
        print(f"Всего продаж: {result.total_sales}")
        print(f"Всего чеков: {result.total_receipts}")
        print(f"Всего QR транзакций: {result.total_transactions}")
        print(f"Успешно сверено: {result.matched_count}")
        print(f"Выявлено несоответствий: {len(result.discrepancies)}")
        
        if result.total_sales > 0:
            success_rate = (result.matched_count / result.total_sales) * 100
            print(f"Процент успешной сверки: {success_rate:.1f}%")
        
        # Топ проблем
        if result.discrepancies:
            print("\nТоп несоответствий:")
            from collections import Counter
            
            discrepancy_types = Counter(d.type.value for d in result.discrepancies)
            for disc_type, count in discrepancy_types.most_common(5):
                print(f"  - {disc_type}: {count}")
        
        print("=" * 60)


def parse_period(period_str: str) -> tuple[datetime, datetime]:
    """Парсинг периода из строки формата YYYY-MM-DD:YYYY-MM-DD"""
    try:
        start_str, end_str = period_str.split(':')
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
        
        # Устанавливаем время начала и конца дня
        period_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return period_start, period_end
    except Exception as e:
        raise ValueError(f"Invalid period format. Use YYYY-MM-DD:YYYY-MM-DD. Error: {e}")


def main():
    """Точка входа"""
    parser = argparse.ArgumentParser(
        description='VendBot Audit Module - Automated reconciliation of vending machine reports'
    )
    
    parser.add_argument(
        '--period',
        required=True,
        help='Period for audit in format YYYY-MM-DD:YYYY-MM-DD'
    )
    
    parser.add_argument(
        '--upload-folder',
        default='./data/',
        help='Folder with input data files (default: ./data/)'
    )
    
    parser.add_argument(
        '--output-folder',
        default='./reports/',
        help='Folder for output reports (default: ./reports/)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Настройка уровня логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Парсинг периода
    try:
        period_start, period_end = parse_period(args.period)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    
    # Проверка папок
    data_folder = Path(args.upload_folder)
    if not data_folder.exists():
        logger.error(f"Data folder not found: {data_folder}")
        sys.exit(1)
    
    output_folder = Path(args.output_folder)
    
    # Запуск аудита
    runner = AuditRunner(data_folder, output_folder)
    runner.run(period_start, period_end)


if __name__ == '__main__':
    main()