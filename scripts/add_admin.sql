-- Добавляем админа если его нет
INSERT INTO users (telegram_id, username, full_name, role, is_active, created_at, updated_at)
VALUES (42283329, 'Jamshiddin', '', 'admin', true, NOW(), NOW())
ON CONFLICT (telegram_id) 
DO UPDATE SET 
    role = 'admin',
    is_active = true,
    updated_at = NOW();
