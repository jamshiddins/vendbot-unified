"""
Скрипт для создания шаблонов входных файлов
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_sales_template():
    """Создание шаблона файла продаж"""
    data = {
        'machine_id': ['1', '1', '2', '2', '3'],
        'datetime': [
            datetime.now() - timedelta(hours=5),
            datetime.now() - timedelta(hours=4),
            datetime.now() - timedelta(hours=3),
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=1)
        ],
        'product_code': ['ESPRESSO', 'CAPPUCCINO', 'AMERICANO', 'LATTE', 'ESPRESSO'],
        'product_name': ['Эспрессо', 'Капучино', 'Американо', 'Латте', 'Эспрессо'],
        'amount': [150, 220, 180, 250, 150],
        'payment_method': ['cash', 'card', 'click', 'payme', 'test'],
        'quantity': [1, 1, 1, 1, 1]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('templates/sales_report_template.xlsx', index=False)
    print("Created: sales_report_template.xlsx")

def create_receipts_template():
    """Создание шаблона файла чеков"""
    data = [
        {
            'receipt_number': 'KKM001234',
            'machine_id': '1',
            'datetime': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'amount': '150',
            'payment_method': 'cash',
            'items': 'Эспрессо:150'
        },
        {
            'receipt_number': 'KKM001235',
            'machine_id': '1',
            'datetime': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
            'amount': '220',
            'payment_method': 'card',
            'items': 'Капучино:220'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_csv('templates/kkm_receipts_template.csv', index=False)
    print("Created: kkm_receipts_template.csv")

def create_qr_templates():
    """Создание шаблонов QR транзакций"""
    # Click
    click_data = {
        'payment_id': ['CLICK123456'],
        'payment_date': [datetime.now() - timedelta(hours=3)],
        'amount': [180],
        'status': ['success'],
        'merchant_trans_id': ['VM_2_ORDER_789']
    }
    
    df = pd.DataFrame(click_data)
    df.to_excel('templates/qr_click_template.xlsx', index=False)
    print("Created: qr_click_template.xlsx")
    
    # Payme
    payme_data = {
        'transaction': ['PAYME789012'],
        'create_time': [datetime.now() - timedelta(hours=2)],
        'amount': [25000],  # в тийинах
        'state': [2],  # успешно
        'order_id': ['machine-2-order-790']
    }
    
    df = pd.DataFrame(payme_data)
    df.to_excel('templates/qr_payme_template.xlsx', index=False)
    print("Created: qr_payme_template.xlsx")

def create_recipes_template():
    """Создание шаблона рецептов"""
    recipes = {
        "recipes": [
            {
                "product_code": "ESPRESSO",
                "product_name": "Эспрессо",
                "category": "coffee",
                "ingredients": [
                    {"code": "COFFEE_ARABICA", "name": "Кофе Арабика", "quantity": 7, "unit": "g"},
                    {"code": "WATER", "name": "Вода", "quantity": 30, "unit": "ml"}
                ]
            },
            {
                "product_code": "CAPPUCCINO",
                "product_name": "Капучино",
                "category": "coffee",
                "ingredients": [
                    {"code": "COFFEE_ARABICA", "name": "Кофе Арабика", "quantity": 7, "unit": "g"},
                    {"code": "MILK_POWDER", "name": "Молоко сухое", "quantity": 20, "unit": "g"},
                    {"code": "WATER", "name": "Вода", "quantity": 150, "unit": "ml"}
                ]
            }
        ]
    }
    
    with open('templates/recipes_template.json', 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    print("Created: recipes_template.json")

if __name__ == '__main__':
    # Создаем папку для шаблонов
    Path('templates').mkdir(exist_ok=True)
    
    # Создаем все шаблоны
    create_sales_template()
    create_receipts_template()
    create_qr_templates()
    create_recipes_template()
    
    print("\nAll templates created successfully!")