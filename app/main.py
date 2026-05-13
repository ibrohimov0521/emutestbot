from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot_commands import set_default_commands
from app.config import settings
from app.database import init_db
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
    if settings.auto_seed_districts:
        from seed import seed_district_questions

        seed_result = await seed_district_questions()
        logging.info(
            "District questions seed completed: inserted=%s skipped=%s total=%s",
            seed_result["inserted"],
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
