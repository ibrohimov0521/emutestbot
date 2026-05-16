from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot_commands import set_chat_commands
from app.config import settings
from app.keyboards import BTN_HELP, BTN_LAST_RESULTS, BTN_PROFILE, main_menu
from app.services import user_service

router = Router()


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


async def _ensure_allowed(message: Message) -> int | None:
    if not message.from_user:
        return None
    try:
        return await user_service.upsert_user(message.from_user)
    except PermissionError:
        await message.answer(user_service.access_denied_text(message.from_user.id))
        return None


def _help_text(is_admin: bool) -> str:
    text = (
        "Yordam\n\n"
        "Botdan foydalanish uchun sizning Telegram ID'ingiz admin tomonidan bazaga qo'shilgan bo'lishi kerak.\n"
        "Testni boshlash uchun \"Testni boshlash\" tugmasini bosing va har bir savolga matn bilan javob yozing.\n\n"
        f"Ruxsat yoki savollar bo'yicha admin: {user_service.ADMIN_CONTACT}"
    )
    if is_admin:
        text += (
            "\n\nAdmin komandalar:\n"
            "/admin - umumiy statistika\n"
            "/users - userlar ro'yxati\n"
            "/add_user TELEGRAM_ID - yangi user qo'shish\n"
            "/block_user TELEGRAM_ID - userni bloklash\n"
            "/unblock_user TELEGRAM_ID - userni qayta aktiv qilish\n"
            "/user_stats USER_ID - user statistikasi\n"
            "/seed_questions - barcha savollarni seed qilish\n"
            "/seed_districts - tuman savollarini seed qilish"
        )
    return text


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await set_chat_commands(message.bot, message.chat.id, _is_admin(message.from_user.id))
    await user_service.log_operation(user_id, "start")
    await message.answer(
        "Assalomu alaykum! EMU TEST BOT ga xush kelibsiz.\n\n"
        "Testni boshlash uchun pastdagi tugmani bosing.",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_PROFILE)
async def profile(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "profile")
    data = await user_service.get_profile(user_id)
    username = f"@{data['username']}" if data.get("username") else "yo'q"
    await message.answer(
        "Profilim\n\n"
        f"Telegram ID: {data['telegram_id']}\n"
        f"Username: {username}\n"
        f"Ism: {data.get('first_name') or '-'}\n"
        f"Rol: {data['role']}\n"
        f"Status: {data['status']}\n"
        f"Ishlangan testlar: {data['tests_count']}\n"
        f"Operatsiyalar: {data['operations_count']}\n"
        f"Ro'yxatdan o'tgan: {data['created_at']}\n"
        f"Oxirgi faollik: {data['last_seen_at']}",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_LAST_RESULTS)
async def last_results(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
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


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_message(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "help")
    await message.answer(_help_text(_is_admin(message.from_user.id)), reply_markup=main_menu())
