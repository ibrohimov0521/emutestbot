from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _parse_admin_ids(value: str) -> set[int]:
    admin_ids: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if item:
            admin_ids.add(int(item))
    return admin_ids


@dataclass(frozen=True)
class Settings:
    bot_token: str
    openai_api_key: str
    openai_model: str
    admin_ids: set[int]
    database_path: Path
    questions_per_test: int = 50


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    db_path = Path(os.getenv("DATABASE_PATH", "data/bot.db"))
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path

    return Settings(
        bot_token=bot_token,
        openai_api_key=openai_api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        database_path=db_path,
        questions_per_test=int(os.getenv("QUESTIONS_PER_TEST", "50")),
    )


settings = get_settings()
