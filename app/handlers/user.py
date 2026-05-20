from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot_commands import set_chat_commands
from app.config import settings
from app.i18n import (
    LANG_CYRL,
    LANG_UZ,
    LANGUAGE_BUTTON_CYRL,
    LANGUAGE_BUTTON_UZ,
    button_values,
    localize_value,
    text,
)
from app.keyboards import language_menu, main_menu
from app.services import user_service
from app.time_utils import format_tashkent

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


async def _help_text_for(user_id: int, is_admin: bool) -> str:
    language = await user_service.get_language(user_id)
    value = text("help", language, admin_contact=user_service.ADMIN_CONTACT)
    if is_admin:
        value += text("admin_commands", language)
    return value


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await set_chat_commands(message.bot, message.chat.id, _is_admin(message.from_user.id))
    await user_service.log_operation(user_id, "start")
    await message.answer(text("choose_language", LANG_UZ), reply_markup=language_menu())


@router.message(F.text.in_({LANGUAGE_BUTTON_UZ, LANGUAGE_BUTTON_CYRL}))
async def choose_language(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = LANG_CYRL if message.text == LANGUAGE_BUTTON_CYRL else LANG_UZ
    await user_service.set_language(user_id, language)
    await user_service.log_operation(user_id, "set_language", {"language": language})
    await message.answer(text("language_saved", language), reply_markup=main_menu(language))
    await message.answer(text("welcome", language), reply_markup=main_menu(language))


@router.message(Command("language"))
@router.message(F.text.in_(button_values("language")))
async def language_settings(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    await user_service.log_operation(user_id, "language_settings")
    await message.answer(text("choose_language", language), reply_markup=language_menu())


@router.message(F.text.in_(button_values("profile")))
async def profile(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "profile")
    data = await user_service.get_profile(user_id)
    language = data.get("language") or LANG_UZ
    username = f"@{data['username']}" if data.get("username") else ""
    username_empty = localize_value("yo'q", language)
    role_label = localize_value("Rol", language)
    status_label = localize_value("Status", language)
    tests_label = localize_value("Ishlangan testlar", language)
    operations_label = localize_value("Operatsiyalar", language)
    created_label = localize_value("Ro'yxatdan o'tgan", language)
    last_seen_label = localize_value("Oxirgi faollik", language)
    username = username if data.get("username") else username_empty
    await message.answer(
        f"{text('profile_title', language)}\n\n"
        f"Telegram ID: {data['telegram_id']}\n"
        f"Username: {username}\n"
        f"Ism: {data.get('first_name') or '-'}\n"
        f"{role_label}: {data['role']}\n"
        f"{status_label}: {data['status']}\n"
        f"{tests_label}: {data['tests_count']}\n"
        f"{operations_label}: {data['operations_count']}\n"
        f"{created_label}: {format_tashkent(data['created_at'])}\n"
        f"{last_seen_label}: {format_tashkent(data['last_seen_at'])}",
        reply_markup=main_menu(language),
    )


@router.message(F.text.in_(button_values("last_results")))
async def last_results(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "last_results")
    language = await user_service.get_language(user_id)
    results = await user_service.get_last_results(user_id)
    if not results:
        await message.answer(text("no_results", language), reply_markup=main_menu(language))
        return

    lines = [text("last_results_title", language)]
    for item in results:
        total = int(item["total_questions"])
        correct = int(item["correct_count"])
        percent = correct / total * 100 if total else 0
        lines.append(
            f"#{item['id']}: {correct}/{total} ({percent:.1f}%) | "
            f"{format_tashkent(item['started_at'])} - {format_tashkent(item['finished_at'])}"
        )
    await message.answer("\n".join(lines), reply_markup=main_menu(language))


@router.message(Command("help"))
@router.message(F.text.in_(button_values("help")))
async def help_message(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "help")
    language = await user_service.get_language(user_id)
    await message.answer(await _help_text_for(user_id, _is_admin(message.from_user.id)), reply_markup=main_menu(language))
