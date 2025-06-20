-- Обновление структуры таблицы users для поддержки множественных ролей
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS roles JSON DEFAULT '[]'::json;

-- Переносим старые роли в новый формат
UPDATE users 
SET roles = 
  CASE 
    WHEN role = 'admin' THEN '["admin"]'::json
    WHEN role = 'warehouse' THEN '["warehouse"]'::json
    WHEN role = 'operator' THEN '["operator"]'::json
    WHEN role = 'driver' THEN '["driver"]'::json
    ELSE '[]'::json
  END
WHERE roles IS NULL;

-- Устанавливаем владельца
UPDATE users 
SET 
  roles = '["admin"]'::json,
  is_active = true
WHERE telegram_id = 42283329;

-- Деактивируем всех остальных по умолчанию
UPDATE users 
SET is_active = false
WHERE telegram_id != 42283329;
