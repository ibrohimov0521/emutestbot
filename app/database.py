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
