from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.keyboards import admin_users_pagination
from app.services import admin_service, user_service
from app.states import AdminStates
from app.time_utils import format_tashkent

router = Router()


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


async def _require_admin(message: Message) -> bool:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer("Bu bo'lim faqat adminlar uchun.")
        return False
    user_id = await user_service.upsert_user(message.from_user)
    await user_service.log_operation(user_id, "admin_command")
    return True


def _parse_telegram_id(command: CommandObject | None) -> int | None:
    if not command or not command.args:
        return None
    value = command.args.strip().split()[0]
    if not value.isdigit():
        return None
    return int(value)


def _parse_message_telegram_id(message: Message) -> int | None:
    value = (message.text or "").strip().split()[0] if message.text else ""
    if not value.isdigit():
        return None
    return int(value)


async def _add_user_by_telegram_id(message: Message, telegram_id: int) -> None:
    user = await user_service.add_allowed_user(telegram_id)
    await message.answer(
        "User qo'shildi yoki aktiv qilindi.\n\n"
        f"Telegram ID: {user['telegram_id']}\n"
        f"Status: {user['status']}\n"
        f"Rol: {user['role']}"
    )


async def _send_user_stats(message: Message, user_id: int) -> None:
    summary = await admin_service.user_summary(user_id)
    if not summary:
        await message.answer("Bunday user topilmadi.")
        return
    total_answers = int(summary["correct"]) + int(summary["wrong"])
    percent = int(summary["correct"]) / total_answers * 100 if total_answers else 0
    username = f"@{summary['username']}" if summary.get("username") else "yo'q"
    await message.answer(
        "User statistikasi\n\n"
        f"ID: {summary['id']}\n"
        f"Telegram ID: {summary['telegram_id']}\n"
        f"Username: {username}\n"
        f"Ism: {summary.get('first_name') or '-'}\n"
        f"Rol: {summary['role']}\n"
        f"Status: {summary['status']}\n"
        f"Oxirgi kirgan: {format_tashkent(summary['last_seen_at'])}\n"
        f"Operatsiyalar: {summary['operations_count']}\n"
        f"Testlar: {summary['sessions']}\n"
        f"Umumiy to'g'ri: {summary['correct']}\n"
        f"Umumiy noto'g'ri: {summary['wrong']}\n"
        f"Umumiy foiz: {percent:.1f}%"
    )


async def _block_user_by_telegram_id(message: Message, telegram_id: int) -> None:
    user = await user_service.set_user_status(telegram_id, "blocked")
    if not user:
        await message.answer("Bunday Telegram ID bazada topilmadi.")
        return
    await message.answer(f"User bloklandi: {telegram_id}")


async def _unblock_user_by_telegram_id(message: Message, telegram_id: int) -> None:
    user = await user_service.set_user_status(telegram_id, "active")
    if not user:
        user = await user_service.add_allowed_user(telegram_id)
    await message.answer(f"User aktiv qilindi: {user['telegram_id']}")


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if not await _require_admin(message):
        return

    stats = await admin_service.dashboard_stats()
    categories = "\n".join(f"- {row['category']}: {row['count']}" for row in stats["categories"]) or "-"
    await message.answer(
        "Admin panel\n\n"
        f"Jami userlar: {stats['total_users']}\n"
        f"Bugun kirgan userlar: {stats['today_users']}\n"
        f"Jami test sessions: {stats['total_sessions']}\n"
        f"Jami tekshirilgan javoblar: {stats['total_answers']}\n"
        f"Savollar soni: {stats['total_questions']}\n"
        f"Aktiv savollar: {stats['active_questions']}\n"
        f"O'zbekiston tumanlari savollari: {stats['district_questions']}\n\n"
        f"Operator yo'riqnomasi savollari: {stats['operator_manual_questions']}\n"
        f"EMU professional test savollari: {stats['professional_questions']}\n\n"
        f"Kategoriya bo'yicha:\n{categories}\n\n"
        "Userlar ro'yxati: /users\n"
        "Yangi user qo'shish: /add_user\n"
        "Userni bloklash: /block_user\n"
        "Userni aktiv qilish: /unblock_user\n"
        "User statistikasi: /user_stats\n"
        "Barcha savollarni seed qilish: /seed_questions\n"
        "Tuman savollarini seed qilish: /seed_districts"
    )


@router.message(Command("users"))
async def users_list(message: Message) -> None:
    if not await _require_admin(message):
        return
    await _send_users_page(message, 1)


async def _send_users_page(message: Message, page: int) -> None:
    users, has_next = await admin_service.list_users(page)
    if not users:
        await message.answer("Userlar topilmadi.")
        return
    lines = [f"Userlar, {page}-sahifa:"]
    for user in users:
        username = f"@{user['username']}" if user.get("username") else "yo'q"
        name = user.get("first_name") or "-"
        lines.append(
            f"#{user['id']} | tg:{user['telegram_id']} | {username} | ism:{name} | "
            f"status:{user['status']} | oxirgi:{format_tashkent(user['last_seen_at'])} | "
            f"test:{user['tests_count']} | op:{user['operations_count']}"
        )
    await message.answer("\n".join(lines), reply_markup=admin_users_pagination(page, page > 1, has_next))


@router.callback_query(F.data.startswith("admin_users:"))
async def users_page_callback(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return
    page = int(callback.data.split(":", 1)[1])
    users, has_next = await admin_service.list_users(page)
    lines = [f"Userlar, {page}-sahifa:"]
    for user in users:
        username = f"@{user['username']}" if user.get("username") else "yo'q"
        name = user.get("first_name") or "-"
        lines.append(
            f"#{user['id']} | tg:{user['telegram_id']} | {username} | ism:{name} | "
            f"status:{user['status']} | oxirgi:{format_tashkent(user['last_seen_at'])} | "
            f"test:{user['tests_count']} | op:{user['operations_count']}"
        )
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_users_pagination(page, page > 1, has_next),
    )
    await callback.answer()


@router.message(Command("user_stats"))
async def user_stats(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not await _require_admin(message):
        return
    if not command.args or not command.args.strip().isdigit():
        await state.set_state(AdminStates.waiting_user_stats_id)
        await message.answer(
            "Statistikasini ko'rish uchun user ID yuboring.\n\n"
            "Masalan: 12\n"
            "Bekor qilish: /cancel"
        )
        return
    await _send_user_stats(message, int(command.args.strip()))


@router.message(Command("add_user"))
async def add_user(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not await _require_admin(message):
        return
    telegram_id = _parse_telegram_id(command)
    if telegram_id is None:
        await state.set_state(AdminStates.waiting_add_user_id)
        await message.answer(
            "Yangi user qo'shish uchun Telegram ID yuboring.\n\n"
            "Masalan: 123456789\n"
            "Bekor qilish: /cancel"
        )
        return
    await _add_user_by_telegram_id(message, telegram_id)


@router.message(AdminStates.waiting_add_user_id, Command("cancel"))
async def cancel_add_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("User qo'shish bekor qilindi.")


@router.message(
    StateFilter(
        AdminStates.waiting_block_user_id,
        AdminStates.waiting_unblock_user_id,
        AdminStates.waiting_user_stats_id,
    ),
    Command("cancel"),
)
async def cancel_admin_action(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Amal bekor qilindi.")


@router.message(AdminStates.waiting_add_user_id)
async def add_user_id_received(message: Message, state: FSMContext) -> None:
    if not await _require_admin(message):
        await state.clear()
        return
    telegram_id = _parse_message_telegram_id(message)
    if telegram_id is None:
        await message.answer("Telegram ID faqat raqamlardan iborat bo'lishi kerak. Qayta yuboring yoki /cancel bosing.")
        return
    await _add_user_by_telegram_id(message, telegram_id)
    await state.clear()


@router.message(AdminStates.waiting_block_user_id)
async def block_user_id_received(message: Message, state: FSMContext) -> None:
    if not await _require_admin(message):
        await state.clear()
        return
    telegram_id = _parse_message_telegram_id(message)
    if telegram_id is None:
        await message.answer("Telegram ID faqat raqamlardan iborat bo'lishi kerak. Qayta yuboring yoki /cancel bosing.")
        return
    await _block_user_by_telegram_id(message, telegram_id)
    await state.clear()


@router.message(AdminStates.waiting_unblock_user_id)
async def unblock_user_id_received(message: Message, state: FSMContext) -> None:
    if not await _require_admin(message):
        await state.clear()
        return
    telegram_id = _parse_message_telegram_id(message)
    if telegram_id is None:
        await message.answer("Telegram ID faqat raqamlardan iborat bo'lishi kerak. Qayta yuboring yoki /cancel bosing.")
        return
    await _unblock_user_by_telegram_id(message, telegram_id)
    await state.clear()


@router.message(AdminStates.waiting_user_stats_id)
async def user_stats_id_received(message: Message, state: FSMContext) -> None:
    if not await _require_admin(message):
        await state.clear()
        return
    user_id = _parse_message_telegram_id(message)
    if user_id is None:
        await message.answer("User ID faqat raqamlardan iborat bo'lishi kerak. Qayta yuboring yoki /cancel bosing.")
        return
    await _send_user_stats(message, user_id)
    await state.clear()


@router.message(Command("block_user"))
async def block_user(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not await _require_admin(message):
        return
    telegram_id = _parse_telegram_id(command)
    if telegram_id is None:
        await state.set_state(AdminStates.waiting_block_user_id)
        await message.answer(
            "Bloklash uchun Telegram ID yuboring.\n\n"
            "Masalan: 123456789\n"
            "Bekor qilish: /cancel"
        )
        return
    await _block_user_by_telegram_id(message, telegram_id)


@router.message(Command("unblock_user"))
async def unblock_user(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not await _require_admin(message):
        return
    telegram_id = _parse_telegram_id(command)
    if telegram_id is None:
        await state.set_state(AdminStates.waiting_unblock_user_id)
        await message.answer(
            "Aktiv qilish uchun Telegram ID yuboring.\n\n"
            "Masalan: 123456789\n"
            "Bekor qilish: /cancel"
        )
        return
    await _unblock_user_by_telegram_id(message, telegram_id)


@router.message(Command("seed_districts"))
async def seed_districts(message: Message) -> None:
    if not await _require_admin(message):
        return

    from seed import seed_district_questions

    result = await seed_district_questions()
    await message.answer(
        "Seed yakunlandi.\n"
        f"Yangi qo'shilgan savollar: {result['inserted']}\n"
        f"Yangilangan savollar: {result.get('updated', 0)}\n"
        f"Avval bor bo'lgan savollar: {result['skipped']}\n"
        f"Jami ishlab chiqilgan savollar: {result['total']}"
    )


@router.message(Command("seed_questions"))
async def seed_questions(message: Message) -> None:
    if not await _require_admin(message):
        return

    from seed import seed_all_questions

    result = await seed_all_questions()
    await message.answer(
        "Barcha savollar seed qilindi.\n"
        f"Yangi qo'shilgan savollar: {result['inserted']}\n"
        f"Yangilangan savollar: {result.get('updated', 0)}\n"
        f"Avval bor bo'lgan savollar: {result['skipped']}\n"
        f"Jami ishlab chiqilgan savollar: {result['total']}"
    )
