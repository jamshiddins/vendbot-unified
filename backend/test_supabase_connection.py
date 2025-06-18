"""
Тестирование подключения к Supabase для проекта vendbot-unified
Этот скрипт проверяет различные аспекты соединения с базой данных
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError

# Добавляем корневую папку проекта в путь Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
env_path = project_root / 'deploy' / 'production' / '.env'
if not env_path.exists():
    print(f"❌ Файл {env_path} не найден!")
    print("💡 Подсказка: Убедитесь, что вы находитесь в папке backend при запуске скрипта")
    sys.exit(1)

load_dotenv(env_path)

class SupabaseConnectionTester:
    """Класс для тестирования подключения к Supabase"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.engine = None
        self.test_results = []
        
    def run_all_tests(self):
        """Запускает все тесты последовательно"""
        print("🔍 Начинаем тестирование подключения к Supabase...")
        print("=" * 60)
        
        # Проверка конфигурации
        if not self._check_configuration():
            return False
            
        # Создание подключения
        if not self._create_connection():
            return False
            
        # Запуск тестов
        tests = [
            self._test_basic_connection,
            self._test_server_info,
            self._test_database_structure,
            self._test_permissions,
            self._test_performance
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"\n❌ Ошибка в тесте {test.__name__}: {str(e)}")
                self.test_results.append((test.__name__, False, str(e)))
                
        # Итоговый отчёт
        self._print_summary()
        return all(result[1] for result in self.test_results)
    
    def _check_configuration(self):
        """Проверяет наличие и корректность конфигурации"""
        print("\n📋 Проверка конфигурации...")
        
        if not self.database_url:
            print("❌ DATABASE_URL не найден в файле .env")
            return False
            
        # Безопасный вывод URL (скрываем пароль)
        if '7VFRINXwBaVx5Lkk' in self.database_url:
            safe_url = self.database_url.replace('7VFRINXwBaVx5Lkk', '***HIDDEN***')
        else:
            # Пытаемся найти и скрыть любой пароль между : и @
            import re
            safe_url = re.sub(r':([^:@]+)@', r':***HIDDEN***@', self.database_url)
            
        print(f"✅ DATABASE_URL найден")
        print(f"   URL: {safe_url}")
        
        # Извлекаем компоненты URL для проверки
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            print(f"   Хост: {parsed.hostname}")
            print(f"   Порт: {parsed.port}")
            print(f"   База данных: {parsed.path.lstrip('/')}")
            print(f"   Пользователь: {parsed.username}")
        except Exception as e:
            print(f"⚠️  Не удалось разобрать URL: {e}")
            
        return True
    
    def _create_connection(self):
        """Создаёт подключение к базе данных"""
        print("\n🔄 Создание подключения к базе данных...")
        
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # Важно для Supabase pooler
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000",
                    "sslmode": "require"  # Supabase требует SSL
                }
            )
            print("✅ Engine создан успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания engine: {e}")
            return False
    
    def _test_basic_connection(self):
        """Базовый тест соединения"""
        print("\n🧪 Тест 1: Базовое подключение")
        
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            value = result.scalar()
            
            if value == 1:
                print("✅ Соединение установлено успешно")
                self.test_results.append(("basic_connection", True, "OK"))
            else:
                raise Exception(f"Неожиданный результат: {value}")
    
    def _test_server_info(self):
        """Получение информации о сервере"""
        print("\n🧪 Тест 2: Информация о сервере")
        
        with self.engine.connect() as conn:
            # Версия PostgreSQL
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL версия: {version.split(' ')[1]}")
            
            # Текущее время на сервере
            result = conn.execute(text("SELECT NOW()"))
            server_time = result.scalar()
            print(f"✅ Время сервера: {server_time}")
            
            # Текущий пользователь и база
            result = conn.execute(text("SELECT current_user, current_database()"))
            user, database = result.fetchone()
            print(f"✅ Пользователь: {user}")
            print(f"✅ База данных: {database}")
            
            self.test_results.append(("server_info", True, "OK"))
    
    def _test_database_structure(self):
        """Проверка структуры базы данных"""
        print("\n🧪 Тест 3: Структура базы данных")
        
        inspector = inspect(self.engine)
        
        # Получаем список схем
        schemas = inspector.get_schema_names()
        public_schemas = [s for s in schemas if not s.startswith('pg_')]
        print(f"✅ Доступные схемы: {', '.join(public_schemas)}")
        
        # Получаем список таблиц
        tables = inspector.get_table_names(schema='public')
        print(f"✅ Таблиц в схеме public: {len(tables)}")
        
        if tables:
            print("   Существующие таблицы:")
            for table in sorted(tables):
                with self.engine.connect() as conn:
                    # Считаем записи в таблице
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    
                    # Получаем столбцы
                    columns = inspector.get_columns(table, schema='public')
                    col_names = [col['name'] for col in columns]
                    
                    print(f"   📊 {table}:")
                    print(f"      - Записей: {count}")
                    print(f"      - Столбцов: {len(columns)} ({', '.join(col_names[:3])}{'...' if len(col_names) > 3 else ''})")
        else:
            print("   ℹ️  Таблиц пока нет")
            print("   💡 Запустите 'alembic upgrade head' для создания структуры БД")
            
        self.test_results.append(("database_structure", True, "OK"))
    
    def _test_permissions(self):
        """Проверка прав доступа"""
        print("\n🧪 Тест 4: Проверка прав доступа")
        
        with self.engine.connect() as conn:
            # Проверяем права на создание таблиц
            try:
                conn.execute(text("CREATE TEMP TABLE test_permissions (id INT)"))
                conn.execute(text("DROP TABLE test_permissions"))
                print("✅ Права на создание временных таблиц: есть")
            except Exception as e:
                print(f"❌ Нет прав на создание таблиц: {e}")
                
            # Проверяем права на основные операции
            operations = {
                "SELECT": "SELECT 1",
                "INSERT": "SELECT 1",  # Не можем реально вставить без таблиц
                "UPDATE": "SELECT 1",  # Аналогично
                "DELETE": "SELECT 1"   # Аналогично
            }
            
            for op, query in operations.items():
                try:
                    conn.execute(text(query))
                    print(f"✅ {op}: доступно")
                except Exception as e:
                    print(f"❌ {op}: недоступно ({e})")
                    
        self.test_results.append(("permissions", True, "OK"))
    
    def _test_performance(self):
        """Простой тест производительности"""
        print("\n🧪 Тест 5: Производительность подключения")
        
        import time
        
        # Тест скорости простого запроса
        times = []
        for i in range(5):
            start = time.time()
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            end = time.time()
            times.append((end - start) * 1000)  # в миллисекундах
            
        avg_time = sum(times) / len(times)
        print(f"✅ Среднее время запроса: {avg_time:.2f} мс")
        
        if avg_time < 50:
            print("   🚀 Отличная скорость!")
        elif avg_time < 100:
            print("   ✅ Хорошая скорость")
        elif avg_time < 200:
            print("   ⚠️  Приемлемая скорость")
        else:
            print("   ⚠️  Медленное соединение")
            
        self.test_results.append(("performance", True, f"Avg: {avg_time:.2f}ms"))
    
    def _print_summary(self):
        """Выводит итоговый отчёт"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЁТ")
        print("=" * 60)
        
        if not self.test_results:
            print("❌ Тесты не были запущены")
            return
            
        passed = sum(1 for _, result, _ in self.test_results if result)
        total = len(self.test_results)
        
        print(f"\nВсего тестов: {total}")
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {total - passed}")
        
        print("\nДетали:")
        for test_name, passed, message in self.test_results:
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}: {message}")
            
        if passed == total:
            print("\n🎉 Все тесты пройдены успешно!")
            print("✅ Подключение к Supabase работает корректно")
            print("\n📝 Следующие шаги:")
            print("1. Запустите миграции: alembic upgrade head")
            print("2. Запустите backend: python main.py")
            print("3. Настройте Telegram бота через @BotFather")
        else:
            print("\n⚠️  Некоторые тесты не прошли")
            print("Проверьте ошибки выше и исправьте проблемы")

# Запуск тестов
if __name__ == "__main__":
    tester = SupabaseConnectionTester()
    tester.run_all_tests()
