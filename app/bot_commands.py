from __future__ import annotations

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


COMMON_COMMANDS = [
    BotCommand(command="start", description="Botni boshlash"),
    BotCommand(command="help", description="Yordam va foydalanish tartibi"),
]

ADMIN_COMMANDS = COMMON_COMMANDS + [
    BotCommand(command="admin", description="Admin panel"),
    BotCommand(command="users", description="Userlar ro'yxati"),
    BotCommand(command="add_user", description="Yangi user qo'shish"),
    BotCommand(command="block_user", description="Userni bloklash"),
    BotCommand(command="unblock_user", description="Userni aktiv qilish"),
    BotCommand(command="user_stats", description="User statistikasi"),
    BotCommand(command="seed_questions", description="Barcha savollarni seed qilish"),
    BotCommand(command="seed_districts", description="Tuman savollarini seed qilish"),
]


async def set_default_commands(bot: Bot) -> None:
    await bot.set_my_commands(COMMON_COMMANDS, scope=BotCommandScopeDefault())


async def set_chat_commands(bot: Bot, chat_id: int, is_admin: bool) -> None:
    commands = ADMIN_COMMANDS if is_admin else COMMON_COMMANDS
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=chat_id))
