from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import aiosqlite

from app.config import settings
from app.models import SCHEMA_SQL


async def init_db() -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(settings.database_path) as db:
        await db.executescript(SCHEMA_SQL)
        columns = await db.execute_fetchall("PRAGMA table_info(users)")
        column_names = {row[1] for row in columns}
        if "status" not in column_names:
            await db.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        if "language" not in column_names:
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT 'uz'")
        question_columns = await db.execute_fetchall("PRAGMA table_info(questions)")
        question_column_names = {row[1] for row in question_columns}
        if "question_type" not in question_column_names:
            await db.execute("ALTER TABLE questions ADD COLUMN question_type TEXT NOT NULL DEFAULT 'text'")
        if "options_json" not in question_column_names:
            await db.execute("ALTER TABLE questions ADD COLUMN options_json TEXT")
        await db.commit()


def get_db_path() -> Path:
    return settings.database_path


async def connect_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(settings.database_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


@asynccontextmanager
async def db_session() -> AsyncIterator[aiosqlite.Connection]:
    db = await connect_db()
    try:
        yield db
    finally:
        await db.close()
