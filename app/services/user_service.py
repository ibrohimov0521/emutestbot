from __future__ import annotations

import json
from typing import Any

from aiogram.types import User as TelegramUser

from app.config import settings
from app.database import db_session


async def upsert_user(tg_user: TelegramUser) -> int:
    role = "admin" if tg_user.id in settings.admin_ids else "user"
    async with db_session() as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, role)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                role = excluded.role,
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name, role),
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
            SELECT id, telegram_id, username, first_name, last_name, role, created_at,
                   last_seen_at, operations_count, tests_count
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )
        return dict(rows[0])


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
