from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.keyboards import admin_users_pagination
from app.services import admin_service, user_service

router = Router()


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    user_id = await user_service.upsert_user(message.from_user)
    await user_service.log_operation(user_id, "admin_panel")
    if not _is_admin(message.from_user.id):
        await message.answer("Bu bo'lim faqat adminlar uchun.")
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
        f"Kategoriya bo'yicha:\n{categories}\n\n"
        "Userlar ro'yxati: /users\n"
        "User statistikasi: /user_stats USER_ID\n"
        "Tuman savollarini seed qilish: /seed_districts"
    )


@router.message(Command("users"))
async def users_list(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Bu bo'lim faqat adminlar uchun.")
        return
    await _send_users_page(message, 1)


async def _send_users_page(message: Message, page: int) -> None:
    users, has_next = await admin_service.list_users(page)
    if not users:
        await message.answer("Userlar topilmadi.")
        return
    lines = [f"Userlar, {page}-sahifa:"]
    for user in users:
        name = user.get("username") or user.get("first_name") or user["telegram_id"]
        lines.append(
            f"#{user['id']} | {name} | oxirgi: {user['last_seen_at']} | "
            f"test: {user['tests_count']} | operatsiya: {user['operations_count']}"
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
        name = user.get("username") or user.get("first_name") or user["telegram_id"]
        lines.append(
            f"#{user['id']} | {name} | oxirgi: {user['last_seen_at']} | "
            f"test: {user['tests_count']} | operatsiya: {user['operations_count']}"
        )
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_users_pagination(page, page > 1, has_next),
    )
    await callback.answer()


@router.message(Command("user_stats"))
async def user_stats(message: Message, command: CommandObject) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Bu bo'lim faqat adminlar uchun.")
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Foydalanish: /user_stats USER_ID\nMasalan: /user_stats 12")
        return
    summary = await admin_service.user_summary(int(command.args.strip()))
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
        f"Oxirgi kirgan: {summary['last_seen_at']}\n"
        f"Operatsiyalar: {summary['operations_count']}\n"
        f"Testlar: {summary['sessions']}\n"
        f"Umumiy to'g'ri: {summary['correct']}\n"
        f"Umumiy noto'g'ri: {summary['wrong']}\n"
        f"Umumiy foiz: {percent:.1f}%"
    )


@router.message(Command("seed_districts"))
async def seed_districts(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Bu komanda faqat adminlar uchun.")
        return

    from seed import seed_district_questions

    result = await seed_district_questions()
    await message.answer(
        "Seed yakunlandi.\n"
        f"Yangi qo'shilgan savollar: {result['inserted']}\n"
        f"Avval bor bo'lgan savollar: {result['skipped']}\n"
        f"Jami ishlab chiqilgan savollar: {result['total']}"
    )
