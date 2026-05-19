from __future__ import annotations

from app.database import db_session


async def dashboard_stats() -> dict:
    async with db_session() as db:
        values = {}
        queries = {
            "total_users": "SELECT COUNT(*) AS count FROM users",
            "today_users": (
                "SELECT COUNT(*) AS count FROM users "
                "WHERE date(last_seen_at, '+5 hours') = date('now', '+5 hours')"
            ),
            "total_sessions": "SELECT COUNT(*) AS count FROM test_sessions",
            "total_answers": "SELECT COUNT(*) AS count FROM test_answers",
            "total_questions": "SELECT COUNT(*) AS count FROM questions",
            "active_questions": "SELECT COUNT(*) AS count FROM questions WHERE is_active = 1",
            "district_questions": (
                "SELECT COUNT(*) AS count FROM questions "
                "WHERE category = 'O''zbekiston tumanlari' AND is_active = 1"
            ),
            "operator_manual_questions": (
                "SELECT COUNT(*) AS count FROM questions "
                "WHERE category = 'Operatorlar yo''riqnomasi 2026' AND is_active = 1"
            ),
        }
        for key, sql in queries.items():
            rows = await db.execute_fetchall(sql)
            values[key] = int(rows[0]["count"])

        category_rows = await db.execute_fetchall(
            "SELECT category, COUNT(*) AS count FROM questions GROUP BY category ORDER BY count DESC"
        )
        values["categories"] = [dict(row) for row in category_rows]
        return values


async def list_users(page: int = 1, per_page: int = 10) -> tuple[list[dict], bool]:
    offset = max(page - 1, 0) * per_page
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT id, telegram_id, username, first_name, last_name, role, last_seen_at,
                   status, operations_count, tests_count
            FROM users
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (per_page + 1, offset),
        )
        users = [dict(row) for row in rows[:per_page]]
        return users, len(rows) > per_page


async def user_summary(user_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT * FROM users WHERE id = ?", (user_id,))
        if not rows:
            return None
        summary = dict(rows[0])
        result_rows = await db.execute_fetchall(
            """
            SELECT COUNT(*) AS sessions,
                   COALESCE(SUM(correct_count), 0) AS correct,
                   COALESCE(SUM(wrong_count), 0) AS wrong
            FROM test_sessions
            WHERE user_id = ? AND status = 'finished'
            """,
            (user_id,),
        )
        summary.update(dict(result_rows[0]))
        return summary


async def user_summary_by_telegram_id(telegram_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        if not rows:
            return None
    return await user_summary(int(rows[0]["id"]))
