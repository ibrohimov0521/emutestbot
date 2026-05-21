from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
RAILWAY_VOLUME_DB_PATH = Path("/data/bot.db")


def _parse_admin_ids(value: str) -> set[int]:
    admin_ids: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if item:
            admin_ids.add(int(item))
    return admin_ids


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_railway_environment() -> bool:
    return any(os.getenv(name) for name in ("RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "RAILWAY_SERVICE_ID"))


def _resolve_database_path() -> Path:
    raw_path = os.getenv("DATABASE_PATH", "data/bot.db").strip() or "data/bot.db"
    db_path = Path(raw_path)
    if (
        _is_railway_environment()
        and not db_path.is_absolute()
        and raw_path.replace("\\", "/") == "data/bot.db"
        and RAILWAY_VOLUME_DB_PATH.parent.exists()
    ):
        return RAILWAY_VOLUME_DB_PATH
    if not db_path.is_absolute():
        return BASE_DIR / db_path
    return db_path


@dataclass(frozen=True)
class Settings:
    bot_token: str
    openai_api_key: str
    openai_model: str
    admin_ids: set[int]
    database_path: Path
    auto_seed_districts: bool
    questions_per_test: int = 30


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    db_path = _resolve_database_path()

    return Settings(
        bot_token=bot_token,
        openai_api_key=openai_api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        database_path=db_path,
        auto_seed_districts=_parse_bool(os.getenv("AUTO_SEED_DISTRICTS", "false")),
        questions_per_test=int(os.getenv("QUESTIONS_PER_TEST", "30")),
    )


settings = get_settings()
