from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot_commands import set_default_commands
from app.config import settings
from app.database import get_db_path, init_db
from app.handlers import admin, test, user


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan.")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY .env faylida ko'rsatilmagan.")

    await init_db()
    logging.info("SQLite database path: %s", get_db_path())
    if settings.auto_seed_districts:
        from seed import seed_all_questions

        seed_result = await seed_all_questions()
        logging.info(
            "Questions seed completed: inserted=%s updated=%s skipped=%s total=%s",
            seed_result["inserted"],
            seed_result.get("updated", 0),
            seed_result["skipped"],
            seed_result["total"],
        )

    bot = Bot(token=settings.bot_token)
    await set_default_commands(bot)
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(test.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
