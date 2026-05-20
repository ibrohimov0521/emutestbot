from __future__ import annotations

import json
from typing import Any

from aiogram.types import User as TelegramUser

from app.config import settings
from app.database import db_session
from app.i18n import LANG_UZ, normalize_language, text

ADMIN_CONTACT = "@Javohir_Ibrohimov"


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


def access_denied_text(telegram_id: int) -> str:
    return text("access_denied", LANG_UZ, admin_contact=ADMIN_CONTACT, telegram_id=telegram_id)


async def get_allowed_user_id(telegram_id: int) -> int | None:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT id
            FROM users
            WHERE telegram_id = ?
              AND status = 'active'
            """,
            (telegram_id,),
        )
        return int(rows[0]["id"]) if rows else None


async def is_allowed(telegram_id: int) -> bool:
    if is_admin(telegram_id):
        return True
    return await get_allowed_user_id(telegram_id) is not None


async def add_allowed_user(telegram_id: int, role: str = "user") -> dict:
    if telegram_id in settings.admin_ids:
        role = "admin"
    async with db_session() as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, role, status, language)
            VALUES (?, ?, 'active', ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                role = excluded.role,
                status = 'active',
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (telegram_id, role, LANG_UZ),
        )
        await db.commit()
    return await get_profile_by_telegram_id(telegram_id) or {}


async def set_user_status(telegram_id: int, status: str) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        if not rows:
            return None
        await db.execute(
            "UPDATE users SET status = ?, last_seen_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (status, telegram_id),
        )
        await db.commit()
    return await get_profile_by_telegram_id(telegram_id)


async def upsert_user(tg_user: TelegramUser) -> int:
    role = "admin" if is_admin(tg_user.id) else "user"
    if not is_admin(tg_user.id) and not await get_allowed_user_id(tg_user.id):
        raise PermissionError(access_denied_text(tg_user.id))
    async with db_session() as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, role, status, language)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                role = excluded.role,
                status = 'active',
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name, role, LANG_UZ),
        )
        await db.commit()
        row = await db.execute_fetchall("SELECT id FROM users WHERE telegram_id = ?", (tg_user.id,))
        return int(row[0]["id"])


async def log_operation(user_id: int, operation_type: str, details: dict[str, Any] | None = None) -> None:
    async with db_session() as db:
        await db.execute(
            "UPDATE users SET operations_count = operations_count + 1, last_seen_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        await db.execute(
            "INSERT INTO user_operations (user_id, operation_type, details) VALUES (?, ?, ?)",
            (user_id, operation_type, json.dumps(details or {}, ensure_ascii=False)),
        )
        await db.commit()


async def get_profile(user_id: int) -> dict:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT id, telegram_id, username, first_name, last_name, role, language, created_at,
                   last_seen_at, status, operations_count, tests_count
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )
        return dict(rows[0])


async def get_profile_by_telegram_id(telegram_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT id, telegram_id, username, first_name, last_name, role, language, created_at,
                   last_seen_at, status, operations_count, tests_count
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )
        return dict(rows[0]) if rows else None


async def get_language(user_id: int) -> str:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT language FROM users WHERE id = ?", (user_id,))
        return normalize_language(rows[0]["language"] if rows else LANG_UZ)


async def set_language(user_id: int, language: str) -> None:
    async with db_session() as db:
        await db.execute(
            "UPDATE users SET language = ?, last_seen_at = CURRENT_TIMESTAMP WHERE id = ?",
            (normalize_language(language), user_id),
        )
        await db.commit()


async def get_last_results(user_id: int, limit: int = 5) -> list[dict]:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT id, started_at, finished_at, total_questions, correct_count, wrong_count, status
            FROM test_sessions
            WHERE user_id = ? AND status = 'finished'
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return [dict(row) for row in rows]
