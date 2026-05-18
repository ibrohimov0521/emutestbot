from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


BTN_START_TEST = "Testni boshlash"
BTN_TEST_DISTRICTS = "Tumanlar bo'yicha"
BTN_TEST_MANUAL = "Ichki nizom va dastur bo'yicha"
BTN_TEST_MIXED = "Aralash"
BTN_TEST_30 = "30 talik test"
BTN_TEST_50 = "50 talik test"
BTN_LAST_RESULTS = "Oxirgi natijalarim"
BTN_PROFILE = "Profilim"
BTN_HELP = "Yordam"
BTN_CANCEL_TEST = "Testni bekor qilish"
BTN_CHOICE_A = "A"
BTN_CHOICE_B = "B"
BTN_CHOICE_C = "C"
BTN_CHOICE_D = "D"

CHOICE_BUTTONS = {BTN_CHOICE_A, BTN_CHOICE_B, BTN_CHOICE_C, BTN_CHOICE_D}


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_START_TEST)],
            [KeyboardButton(text=BTN_LAST_RESULTS), KeyboardButton(text=BTN_PROFILE)],
            [KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
    )


def test_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL_TEST)]],
        resize_keyboard=True,
    )


def choice_answer_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_CHOICE_A),
                KeyboardButton(text=BTN_CHOICE_B),
                KeyboardButton(text=BTN_CHOICE_C),
                KeyboardButton(text=BTN_CHOICE_D),
            ],
            [KeyboardButton(text=BTN_CANCEL_TEST)],
        ],
        resize_keyboard=True,
    )


def test_direction_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TEST_DISTRICTS)],
            [KeyboardButton(text=BTN_TEST_MANUAL)],
            [KeyboardButton(text=BTN_TEST_MIXED)],
            [KeyboardButton(text=BTN_CANCEL_TEST)],
        ],
        resize_keyboard=True,
    )


def test_size_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TEST_30), KeyboardButton(text=BTN_TEST_50)],
            [KeyboardButton(text=BTN_CANCEL_TEST)],
        ],
        resize_keyboard=True,
    )


def admin_users_pagination(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if has_prev:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users:{page - 1}"))
    if has_next:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"admin_users:{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
