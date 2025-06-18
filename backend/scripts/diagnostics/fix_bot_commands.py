import re

# Читаем файл
with open('main_with_handler_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, импортирован ли BotCommand
if 'BotCommand' not in content:
    # Находим строку с импортами из aiogram.types
    import_pattern = r'(from aiogram\.types import .*)'
    match = re.search(import_pattern, content)
    if match:
        old_import = match.group(1)
        # Добавляем BotCommand к импортам
        if 'BotCommand' not in old_import:
            new_import = old_import.rstrip() + ', BotCommand'
            content = content.replace(old_import, new_import)

# Заменяем старый формат команд на новый
old_commands = r'''await bot\.set_my_commands\(\[
            \("start", ".*?"\),
            \("help", ".*?"\),
            \("menu", ".*?"\),
            \("status", ".*?"\),
            \("stats", ".*?"\),
            \("feedback", ".*?"\),
            \("cancel", ".*?"\),
            \("about", ".*?"\)
        \]\)'''

new_commands = '''await bot.set_my_commands([
            BotCommand(command="start", description="Начало работы"),
            BotCommand(command="help", description="Справка"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="status", description="Статус системы"),
            BotCommand(command="stats", description="Статистика"),
            BotCommand(command="feedback", description="Обратная связь"),
            BotCommand(command="cancel", description="Отмена операции"),
            BotCommand(command="about", description="О системе")
        ])'''

# Заменяем
content = re.sub(old_commands, new_commands, content, flags=re.DOTALL)

# Сохраняем исправленный файл
with open('main_with_handler_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(" Файл исправлен!")
