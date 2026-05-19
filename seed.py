from __future__ import annotations

import asyncio
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from app.database import db_session, init_db

BASE_DIR = Path(__file__).resolve().parent
DISTRICTS_PATH = BASE_DIR / "data" / "uzbekistan_districts.json"
OPERATOR_MANUAL_QUESTIONS_PATH = BASE_DIR / "data" / "operator_manual_questions.json"
DISTRICT_CATEGORY = "O'zbekiston tumanlari"


def build_district_questions() -> list[dict[str, Any]]:
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
                    "question_type": "text",
                    "options": [],
                }
            )
    return questions


def _seed_from_text(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def _build_choice_options(question: dict[str, Any], answer_pool: list[str]) -> list[str]:
    correct_answer = str(question["correct_answer"])
    distractors = [answer for answer in dict.fromkeys(answer_pool) if answer != correct_answer]
    rng = random.Random(_seed_from_text(question["question_text"]))
    rng.shuffle(distractors)
    options = [correct_answer, *distractors[:3]]
    rng.shuffle(options)
    return options


def build_operator_manual_questions() -> list[dict[str, Any]]:
    questions = json.loads(OPERATOR_MANUAL_QUESTIONS_PATH.read_text(encoding="utf-8"))
    answer_pool = [str(question["correct_answer"]) for question in questions]
    for question in questions:
        question["question_type"] = "choice"
        options = [str(option) for option in question.get("options", [])]
        if len(options) == 4 and str(question["correct_answer"]) in options:
            question["options"] = options
        else:
            question["options"] = _build_choice_options(question, answer_pool)
    return questions


def build_questions() -> list[dict[str, Any]]:
    return build_district_questions() + build_operator_manual_questions()


async def seed_questions(questions: list[dict[str, Any]], reset_categories: list[str] | None = None) -> dict[str, int]:
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
                SELECT correct_answer, category, difficulty, question_type, options_json, is_active
                FROM questions
                WHERE question_text = ?
                """,
                (question["question_text"],),
            )
            difficulty = question.get("difficulty", "easy")
            question_type = question.get("question_type", "text")
            options_json = json.dumps(question.get("options") or [], ensure_ascii=False)
            if not existing_rows:
                inserted += 1
            else:
                existing = dict(existing_rows[0])
                desired = {
                    "correct_answer": question["correct_answer"],
                    "category": question["category"],
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "options_json": options_json,
                    "is_active": 1,
                }
                if existing == desired:
                    skipped += 1
                else:
                    updated += 1

            await db.execute(
                """
                INSERT INTO questions (
                    question_text, correct_answer, category, difficulty, question_type, options_json, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(question_text) DO UPDATE SET
                    correct_answer = excluded.correct_answer,
                    category = excluded.category,
                    difficulty = excluded.difficulty,
                    question_type = excluded.question_type,
                    options_json = excluded.options_json,
                    is_active = 1
                """,
                (
                    question["question_text"],
                    question["correct_answer"],
                    question["category"],
                    difficulty,
                    question_type,
                    options_json,
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
