#!/usr/bin/env python3
"""
Скрипт для автоматического исправления всех импортов в проекте
Удаляет префикс 'backend.' из всех импортов
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Исправляет импорты в одном файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Не могу прочитать {filepath}: {e}")
        return False
    
    original_content = content
    
    # Паттерны для замены
    replacements = [
        # from backend.xxx -> from xxx
        (r'from backend\.', r'from '),
        # import backend.xxx -> import xxx
        (r'import backend\.', r'import '),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Сохраняем только если были изменения
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Исправлен: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Не могу записать {filepath}: {e}")
            return False
    return False

def main():
    """Основная функция"""
    backend_dir = Path(__file__).parent.parent
    fixed_count = 0
    error_count = 0
    
    print("🔍 Поиск Python файлов для исправления...")
    
    # Находим все .py файлы
    py_files = list(backend_dir.rglob("*.py"))
    print(f"📁 Найдено {len(py_files)} Python файлов")
    
    for py_file in py_files:
        # Пропускаем файлы в archive и __pycache__
        if 'archive' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        # Пропускаем сам этот скрипт
        if py_file.name == 'fix_all_imports.py':
            continue
            
        if fix_imports_in_file(py_file):
            fixed_count += 1
        else:
            # Проверяем, были ли ошибки
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    if 'from backend.' in f.read() or 'import backend.' in f.read():
                        error_count += 1
            except:
                pass
    
    print(f"\n📊 Результаты:")
    print(f"✅ Исправлено файлов: {fixed_count}")
    print(f"⚠️  Файлов с потенциальными проблемами: {error_count}")
    print(f"📁 Всего проверено: {len(py_files)}")

if __name__ == "__main__":
    main()
