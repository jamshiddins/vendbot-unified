from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
import subprocess
import asyncio

from db.models.user import UserRole
from bot.filters import RoleFilter

router = Router(name="admin_audit")

@router.message(F.text == "📊 Запустить аудит", RoleFilter(UserRole.ADMIN))
async def start_audit(message: Message, state: FSMContext):
    """Запуск аудита через Telegram"""
    await message.answer(
        "🔍 Запуск аудита...\n"
        "Это может занять несколько минут."
    )
    
    try:
        # Запускаем аудит в отдельном процессе
        process = await asyncio.create_subprocess_exec(
            'python', '-m', 'src.audit.main',
            '--period', '2025-06-01:2025-06-15',
            '--upload-folder', './audit_data/',
            '--output-folder', './audit_reports/',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Отправляем отчет
            report_files = list(Path('./audit_reports/').glob('audit_report_*.xlsx'))
            if report_files:
                latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                
                await message.answer_document(
                    FSInputFile(latest_report),
                    caption="✅ Аудит завершен успешно!"
                )
            else:
                await message.answer("⚠️ Аудит завершен, но отчет не найден.")
        else:
            await message.answer(
                f"❌ Ошибка при выполнении аудита:\n"
                f"```\n{stderr.decode()[-500:]}\n```",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")