import asyncio
import sys
sys.path.insert(0, "backend")

from sqlalchemy import text
from db.database import engine

async def create_roles_table():
    """Создаем таблицу для множественных ролей"""
    
    async with engine.begin() as conn:
        # Создаем таблицу user_role_assignments
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_role_assignments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                assigned_by INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, role)
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_role_assignments(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_roles_active ON user_role_assignments(is_active);
        """))
        
        print(" Таблица user_role_assignments создана")

if __name__ == "__main__":
    asyncio.run(create_roles_table())
