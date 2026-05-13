from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards import BTN_LAST_RESULTS, BTN_PROFILE, main_menu
from app.services import user_service

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = await user_service.upsert_user(message.from_user)
    await user_service.log_operation(user_id, "start")
    await message.answer(
        "Assalomu alaykum! EMU TEST BOT ga xush kelibsiz.\n\n"
        "Testni boshlash uchun pastdagi tugmani bosing.",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_PROFILE)
async def profile(message: Message) -> None:
    user_id = await user_service.upsert_user(message.from_user)
    await user_service.log_operation(user_id, "profile")
    data = await user_service.get_profile(user_id)
    username = f"@{data['username']}" if data.get("username") else "yo'q"
    await message.answer(
        "Profilim\n\n"
        f"Telegram ID: {data['telegram_id']}\n"
        f"Username: {username}\n"
        f"Ism: {data.get('first_name') or '-'}\n"
        f"Rol: {data['role']}\n"
        f"Ishlangan testlar: {data['tests_count']}\n"
        f"Operatsiyalar: {data['operations_count']}\n"
        f"Ro'yxatdan o'tgan: {data['created_at']}\n"
        f"Oxirgi faollik: {data['last_seen_at']}",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_LAST_RESULTS)
async def last_results(message: Message) -> None:
    user_id = await user_service.upsert_user(message.from_user)
    await user_service.log_operation(user_id, "last_results")
    results = await user_service.get_last_results(user_id)
    if not results:
        await message.answer("Hozircha yakunlangan testlaringiz yo'q.", reply_markup=main_menu())
        return

    lines = ["Oxirgi natijalar:"]
    for item in results:
        total = int(item["total_questions"])
        correct = int(item["correct_count"])
        percent = correct / total * 100 if total else 0
        lines.append(
            f"#{item['id']}: {correct}/{total} ({percent:.1f}%) | "
            f"{item['started_at']} - {item['finished_at']}"
        )
    await message.answer("\n".join(lines), reply_markup=main_menu())
