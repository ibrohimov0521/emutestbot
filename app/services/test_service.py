from __future__ import annotations

import json

from app.database import db_session
from app.i18n import LANG_UZ, localize_value, text
from app.services.openai_checker import CheckResult
from app.time_utils import format_tashkent

DISTRICT_CATEGORY = "O'zbekiston tumanlari"
OPERATOR_MANUAL_CATEGORY = "Operatorlar yo'riqnomasi 2026"
TEST_DIRECTION_DISTRICTS = "districts"
TEST_DIRECTION_MANUAL = "manual"
TEST_DIRECTION_MIXED = "mixed"
QUESTION_TYPE_TEXT = "text"
QUESTION_TYPE_CHOICE = "choice"
CHOICE_LABELS = ("A", "B", "C", "D")


async def get_active_session(user_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            "SELECT * FROM test_sessions WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        return dict(rows[0]) if rows else None


async def start_test(user_id: int, total_questions: int, direction: str = TEST_DIRECTION_MIXED) -> dict:
    active = await get_active_session(user_id)
    if active:
        return active

    async with db_session() as db:
        where_sql = "WHERE is_active = 1"
        params: tuple[object, ...] = (total_questions,)
        if direction == TEST_DIRECTION_DISTRICTS:
            where_sql = "WHERE is_active = 1 AND category = ?"
            params = (DISTRICT_CATEGORY, total_questions)
        elif direction == TEST_DIRECTION_MANUAL:
            where_sql = "WHERE is_active = 1 AND category = ?"
            params = (OPERATOR_MANUAL_CATEGORY, total_questions)

        question_rows = await db.execute_fetchall(
            f"""
            SELECT id
            FROM questions
            {where_sql}
            ORDER BY RANDOM()
            LIMIT ?
            """,
            params,
        )
        if len(question_rows) < total_questions:
            raise ValueError(f"Kamida {total_questions} ta aktiv savol kerak.")

        cursor = await db.execute(
            "INSERT INTO test_sessions (user_id, total_questions) VALUES (?, ?)",
            (user_id, total_questions),
        )
        session_id = cursor.lastrowid
        for position, row in enumerate(question_rows, start=1):
            await db.execute(
                """
                INSERT INTO test_session_questions (session_id, question_id, position)
                VALUES (?, ?, ?)
                """,
                (session_id, row["id"], position),
            )
        await db.commit()
        return (await get_session(session_id)) or {}


async def get_session(session_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT * FROM test_sessions WHERE id = ?", (session_id,))
        return dict(rows[0]) if rows else None


async def get_next_question(session_id: int) -> dict | None:
    async with db_session() as db:
        rows = await db.execute_fetchall(
            """
            SELECT q.*, tsq.position
            FROM test_session_questions tsq
            JOIN questions q ON q.id = tsq.question_id
            LEFT JOIN test_answers ta
                ON ta.session_id = tsq.session_id AND ta.question_id = tsq.question_id
            WHERE tsq.session_id = ? AND ta.id IS NULL
            ORDER BY tsq.position
            LIMIT 1
            """,
            (session_id,),
        )
        return dict(rows[0]) if rows else None


def is_choice_question(question: dict) -> bool:
    return question.get("question_type") == QUESTION_TYPE_CHOICE


def get_choice_options(question: dict) -> list[str]:
    if not is_choice_question(question):
        return []
    if isinstance(question.get("options"), list):
        return [str(option) for option in question["options"][:4]]
    try:
        options = json.loads(question.get("options_json") or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(options, list):
        return []
    return [str(option) for option in options[:4]]


def display_text(value: str, language: str = LANG_UZ) -> str:
    return localize_value(value, language)


def format_question_text(question: dict, answered_count: int, total_questions: int, language: str = LANG_UZ) -> str:
    counter = text("question_counter", language, current=answered_count + 1, total=total_questions)
    base = f"{counter}\n\n{display_text(question['question_text'], language)}"
    options = get_choice_options(question)
    if not options:
        return base

    option_lines = [f"{label}) {display_text(option, language)}" for label, option in zip(CHOICE_LABELS, options)]
    return f"{base}\n\n" + "\n".join(option_lines)


def check_choice_answer(question: dict, user_answer: str, language: str = LANG_UZ) -> CheckResult | None:
    selected = user_answer.strip().upper()
    options = get_choice_options(question)
    if selected not in CHOICE_LABELS or len(options) < 4:
        return None

    selected_index = CHOICE_LABELS.index(selected)
    selected_answer = options[selected_index]
    is_correct = selected_answer == question["correct_answer"]
    reason = (
        text("correct_choice", language)
        if is_correct
        else text("correct_answer", language, answer=display_text(question["correct_answer"], language))
    )
    return CheckResult(is_correct=is_correct, score=1.0 if is_correct else 0.0, reason=reason)


def format_choice_user_answer(question: dict, user_answer: str) -> str:
    selected = user_answer.strip().upper()
    options = get_choice_options(question)
    if selected in CHOICE_LABELS and len(options) >= 4:
        return f"{selected}. {options[CHOICE_LABELS.index(selected)]}"
    return user_answer


async def count_answered(session_id: int) -> int:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT COUNT(*) AS count FROM test_answers WHERE session_id = ?", (session_id,))
        return int(rows[0]["count"])


async def save_answer(session_id: int, question: dict, user_answer: str, result: CheckResult) -> dict:
    async with db_session() as db:
        await db.execute(
            """
            INSERT INTO test_answers (
                session_id, question_id, user_answer, correct_answer, is_correct, ai_score, ai_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                question["id"],
                user_answer,
                question["correct_answer"],
                int(result.is_correct),
                result.score,
                result.reason,
            ),
        )
        if result.is_correct:
            await db.execute(
                "UPDATE test_sessions SET correct_count = correct_count + 1 WHERE id = ?",
                (session_id,),
            )
        else:
            await db.execute(
                "UPDATE test_sessions SET wrong_count = wrong_count + 1 WHERE id = ?",
                (session_id,),
            )
        await db.commit()

    session = await get_session(session_id)
    if session and session["correct_count"] + session["wrong_count"] >= session["total_questions"]:
        await finish_session(session_id)
        session = await get_session(session_id)
    return session or {}


async def finish_session(session_id: int) -> None:
    async with db_session() as db:
        rows = await db.execute_fetchall("SELECT user_id FROM test_sessions WHERE id = ?", (session_id,))
        if not rows:
            return
        user_id = int(rows[0]["user_id"])
        await db.execute(
            "UPDATE test_sessions SET status = 'finished', finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        await db.execute("UPDATE users SET tests_count = tests_count + 1 WHERE id = ?", (user_id,))
        await db.commit()


async def cancel_active_session(user_id: int) -> bool:
    active = await get_active_session(user_id)
    if not active:
        return False
    async with db_session() as db:
        await db.execute(
            "UPDATE test_sessions SET status = 'cancelled', finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            (active["id"],),
        )
        await db.commit()
    return True


def format_result(session: dict, language: str = LANG_UZ) -> str:
    total = int(session["total_questions"])
    correct = int(session["correct_count"])
    wrong = int(session["wrong_count"])
    percent = (correct / total * 100) if total else 0
    if language == "cyrl":
        return (
            f"{text('result_title', language)}\n\n"
            f"Тўғри жавоблар: {correct}\n"
            f"Нотўғри жавоблар: {wrong}\n"
            f"Фоиз: {percent:.1f}%\n"
            f"Бошланиш вақти: {format_tashkent(session['started_at'])}\n"
            f"Тугаш вақти: {format_tashkent(session['finished_at'])}"
        )
    return (
        f"{text('result_title', language)}\n\n"
        f"To'g'ri javoblar: {correct}\n"
        f"Noto'g'ri javoblar: {wrong}\n"
        f"Foiz: {percent:.1f}%\n"
        f"Boshlanish vaqti: {format_tashkent(session['started_at'])}\n"
        f"Tugash vaqti: {format_tashkent(session['finished_at'])}"
    )
