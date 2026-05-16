from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.database import db_session, init_db

BASE_DIR = Path(__file__).resolve().parent
DISTRICTS_PATH = BASE_DIR / "data" / "uzbekistan_districts.json"
OPERATOR_MANUAL_QUESTIONS_PATH = BASE_DIR / "data" / "operator_manual_questions.json"
DISTRICT_CATEGORY = "O'zbekiston tumanlari"


def build_district_questions() -> list[dict[str, str]]:
    data = json.loads(DISTRICTS_PATH.read_text(encoding="utf-8"))
    questions: list[dict[str, str]] = []
    for item in data:
        region = item["region"]
        for district in item["districts"]:
            questions.append(
                {
                    "question_text": f"{district} qaysi viloyatda joylashgan?",
                    "correct_answer": region,
                    "category": DISTRICT_CATEGORY,
                    "difficulty": "easy",
                }
            )
    return questions


def build_operator_manual_questions() -> list[dict[str, str]]:
    return json.loads(OPERATOR_MANUAL_QUESTIONS_PATH.read_text(encoding="utf-8"))


def build_questions() -> list[dict[str, str]]:
    return build_district_questions() + build_operator_manual_questions()


async def seed_questions(questions: list[dict[str, str]], reset_categories: list[str] | None = None) -> dict[str, int]:
    await init_db()
    inserted = 0
    skipped = 0
    updated = 0
    async with db_session() as db:
        for category in reset_categories or []:
            await db.execute("UPDATE questions SET is_active = 0 WHERE category = ?", (category,))
        for question in questions:
            existing_rows = await db.execute_fetchall(
                """
                SELECT correct_answer, category, difficulty, is_active
                FROM questions
                WHERE question_text = ?
                """,
                (question["question_text"],),
            )
            difficulty = question.get("difficulty", "easy")
            if not existing_rows:
                inserted += 1
            else:
                existing = dict(existing_rows[0])
                desired = {
                    "correct_answer": question["correct_answer"],
                    "category": question["category"],
                    "difficulty": difficulty,
                    "is_active": 1,
                }
                if existing == desired:
                    skipped += 1
                else:
                    updated += 1

            await db.execute(
                """
                INSERT INTO questions (
                    question_text, correct_answer, category, difficulty, is_active
                )
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(question_text) DO UPDATE SET
                    correct_answer = excluded.correct_answer,
                    category = excluded.category,
                    difficulty = excluded.difficulty,
                    is_active = 1
                """,
                (
                    question["question_text"],
                    question["correct_answer"],
                    question["category"],
                    difficulty,
                ),
            )
        await db.commit()
    return {"inserted": inserted, "updated": updated, "skipped": skipped, "total": len(questions)}


async def seed_district_questions() -> dict[str, int]:
    return await seed_questions(build_district_questions(), [DISTRICT_CATEGORY])


async def seed_all_questions() -> dict[str, int]:
    return await seed_questions(
        build_questions(),
        [DISTRICT_CATEGORY, "Operatorlar yo'riqnomasi 2026"],
    )


async def main() -> None:
    result = await seed_all_questions()
    print(
        "Seed yakunlandi: "
        f"inserted={result['inserted']}, updated={result['updated']}, "
        f"skipped={result['skipped']}, total={result['total']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
