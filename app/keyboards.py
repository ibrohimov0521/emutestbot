from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from app.i18n import LANGUAGE_BUTTON_CYRL, LANGUAGE_BUTTON_UZ, button


BTN_START_TEST = "Testni boshlash"
BTN_TEST_SIMPLE_MIXED = "Sodda aralash"
BTN_TEST_COMPLEX_MIXED = "Murakkab aralash"
BTN_TEST_DISTRICTS = "Tumanlar bo'yicha"
BTN_TEST_WORK_PROCESS = "Ish jarayoni bo'yicha"
BTN_TEST_30 = "30 talik test"
BTN_TEST_50 = "50 talik test"
BTN_LAST_RESULTS = "Oxirgi natijalarim"
BTN_PROFILE = "Profilim"
BTN_HELP = "Yordam"
BTN_LANGUAGE = "Tilni o'zgartirish"
BTN_CANCEL_TEST = "Testni bekor qilish"
BTN_CHOICE_A = "A"
BTN_CHOICE_B = "B"
BTN_CHOICE_C = "C"
BTN_CHOICE_D = "D"

CHOICE_BUTTONS = {BTN_CHOICE_A, BTN_CHOICE_B, BTN_CHOICE_C, BTN_CHOICE_D}


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=LANGUAGE_BUTTON_UZ), KeyboardButton(text=LANGUAGE_BUTTON_CYRL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button("start_test", language))],
            [KeyboardButton(text=button("last_results", language)), KeyboardButton(text=button("profile", language))],
            [KeyboardButton(text=button("language", language)), KeyboardButton(text=button("help", language))],
        ],
        resize_keyboard=True,
    )


def test_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button("cancel_test", language))]],
        resize_keyboard=True,
    )


def choice_answer_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_CHOICE_A),
                KeyboardButton(text=BTN_CHOICE_B),
                KeyboardButton(text=BTN_CHOICE_C),
                KeyboardButton(text=BTN_CHOICE_D),
            ],
            [KeyboardButton(text=button("cancel_test", language))],
        ],
        resize_keyboard=True,
    )


def test_direction_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button("test_simple_mixed", language))],
            [KeyboardButton(text=button("test_complex_mixed", language))],
            [KeyboardButton(text=button("test_districts", language))],
            [KeyboardButton(text=button("test_work_process", language))],
            [KeyboardButton(text=button("cancel_test", language))],
        ],
        resize_keyboard=True,
    )


def test_size_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button("test_30", language)), KeyboardButton(text=button("test_50", language))],
            [KeyboardButton(text=button("cancel_test", language))],
        ],
        resize_keyboard=True,
    )


def admin_users_pagination(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if has_prev:
        buttons.append(InlineKeyboardButton(text="Oldingi", callback_data=f"admin_users:{page - 1}"))
    if has_next:
        buttons.append(InlineKeyboardButton(text="Keyingi", callback_data=f"admin_users:{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
