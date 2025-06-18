# VendBot Audit Module - Руководство пользователя

## 📋 Описание

Модуль аудита VendBot предназначен для автоматической сверки данных о продажах, платежах и расходе ингредиентов в вендинговых автоматах.

## 🎯 Возможности

- ✅ Сверка продаж с фискальными чеками
- ✅ Сверка QR-платежей (Click, Payme, Uzum)
- ✅ Анализ расхода ингредиентов
- ✅ Выявление несоответствий и аномалий
- ✅ Генерация детальных Excel отчетов

## 📁 Структура входных данных

### Необходимые файлы

1. **sales_report.xlsx** - Отчет о продажах
   - Колонки: machine_id, datetime, product_code, product_name, amount, payment_method, quantity

2. **kkm_receipts.csv** - Фискальные чеки
   - Колонки: receipt_number, machine_id, datetime, amount, payment_method, items

3. **qr_click.xlsx** - Транзакции Click
   - Колонки: payment_id, payment_date, amount, status, merchant_trans_id

4. **qr_payme.xlsx** - Транзакции Payme
   - Колонки: transaction, create_time, amount, state, order_id

5. **qr_uzum.xlsx** - Транзакции Uzum
   - Колонки: trans_id, created_at, amount, status, external_id

6. **recipes.json** - Рецепты напитков
   - Формат: JSON с составом каждого напитка

## 🚀 Запуск

### Базовый запуск

```bash
python -m src.audit.main --period 2025-06-01:2025-06-15 --upload-folder ./data/