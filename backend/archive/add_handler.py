import re

# Читаем файл
with open('main_stable.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Новый обработчик
new_handler = '''
@dp.message()
async def handle_any_message(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "❓ Я не понимаю эту команду.\\n\\n"
        "Используйте /help для списка доступных команд\\n"
        "Или /menu для главного меню",
        parse_mode="HTML"
    )

'''

# Находим место для вставки (перед async def start_bot)
pattern = r'(\n)(async def start_bot)'
replacement = f'\n{new_handler}\\1\\2'

# Проверяем, не добавлен ли уже обработчик
if '@dp.message()' not in content:
    # Делаем замену
    new_content = re.sub(pattern, replacement, content)
    
    # Сохраняем обратно
    with open('main_stable.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Обработчик добавлен успешно!")
else:
    print("⚠️ Обработчик уже существует!")
