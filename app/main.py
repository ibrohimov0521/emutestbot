from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

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

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(test.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
