from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


BTN_START_TEST = "Testni boshlash"
BTN_LAST_RESULTS = "Oxirgi natijalarim"
BTN_PROFILE = "Profilim"
BTN_CANCEL_TEST = "Testni bekor qilish"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_START_TEST)],
            [KeyboardButton(text=BTN_LAST_RESULTS), KeyboardButton(text=BTN_PROFILE)],
        ],
        resize_keyboard=True,
    )


def test_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL_TEST)]],
        resize_keyboard=True,
    )


def admin_users_pagination(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if has_prev:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users:{page - 1}"))
    if has_next:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"admin_users:{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
