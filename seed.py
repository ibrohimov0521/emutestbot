from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.database import db_session, init_db

BASE_DIR = Path(__file__).resolve().parent
DISTRICTS_PATH = BASE_DIR / "data" / "uzbekistan_districts.json"
CATEGORY = "O'zbekiston tumanlari"


def build_questions() -> list[dict[str, str]]:
    data = json.loads(DISTRICTS_PATH.read_text(encoding="utf-8"))
    questions: list[dict[str, str]] = []
    for item in data:
        region = item["region"]
        for district in item["districts"]:
            questions.append(
                {
                    "question_text": f"{district} qaysi viloyatda joylashgan?",
                    "correct_answer": region,
                    "category": CATEGORY,
                    "difficulty": "easy",
                }
            )
    return questions


async def seed_district_questions() -> dict[str, int]:
    await init_db()
    questions = build_questions()
    inserted = 0
    skipped = 0
    async with db_session() as db:
        for question in questions:
            cursor = await db.execute(
                """
                INSERT OR IGNORE INTO questions (
                    question_text, correct_answer, category, difficulty, is_active
                )
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    question["question_text"],
                    question["correct_answer"],
                    question["category"],
                    question["difficulty"],
                ),
            )
            if cursor.rowcount:
                inserted += 1
            else:
                skipped += 1
        await db.commit()
    return {"inserted": inserted, "skipped": skipped, "total": len(questions)}


async def main() -> None:
    result = await seed_district_questions()
    print(
        "Seed yakunlandi: "
        f"inserted={result['inserted']}, skipped={result['skipped']}, total={result['total']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
