# ✅ Создание ингредиента
Invoke-RestMethod -Uri "http://localhost:8000/api/v2/ingredients" -Method POST -ContentType "application/json" -Body '{
  "code": "COFFEE-001",
  "name": "Кофе Арабика",
  "unit": "кг",
  "current_stock": 50.0,
  "min_stock": 10.0,
  "cost": 1500.0
}'

# ✅ Создание бункера
Invoke-RestMethod -Uri "http://localhost:8000/api/v2/assets" -Method POST -ContentType "application/json" -Body '{
  "type": "hopper",
  "inventory_number": "HOP-000001",
  "name": "Бункер №1",
  "status": "active"
}'

# ✅ Создание машины
Invoke-RestMethod -Uri "http://localhost:8000/api/v2/assets" -Method POST -ContentType "application/json" -Body '{
  "type": "machine",
  "inventory_number": "MCH-000001",
  "name": "Кофемашина Ташкент-1",
  "location": "ТЦ Мега Планет, 1 этаж",
  "status": "active"
}'
