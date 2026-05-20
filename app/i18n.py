from __future__ import annotations

LANG_UZ = "uz"
LANG_CYRL = "cyrl"
SUPPORTED_LANGUAGES = {LANG_UZ, LANG_CYRL}

LANGUAGE_BUTTON_UZ = "UZB"
LANGUAGE_BUTTON_CYRL = "КРИЛ"


TEXTS = {
    "choose_language": {
        LANG_UZ: "Tilni tanlang:",
        LANG_CYRL: "Тилни танланг:",
    },
    "language_saved": {
        LANG_UZ: "Til saqlandi.",
        LANG_CYRL: "Тил сақланди.",
    },
    "welcome": {
        LANG_UZ: "Assalomu alaykum! EMU TEST BOT ga xush kelibsiz.\n\nTestni boshlash uchun pastdagi tugmani bosing.",
        LANG_CYRL: "Ассалому алайкум! EMU TEST BOT га хуш келибсиз.\n\nТестни бошлаш учун пастдаги тугмани босинг.",
    },
    "help": {
        LANG_UZ: (
            "Yordam\n\n"
            "Botdan foydalanish uchun sizning Telegram ID'ingiz admin tomonidan bazaga qo'shilgan bo'lishi kerak.\n"
            "Testni boshlash uchun \"Testni boshlash\" tugmasini bosing va ko'rsatmaga amal qiling.\n\n"
            "Ruxsat yoki savollar bo'yicha admin: {admin_contact}"
        ),
        LANG_CYRL: (
            "Ёрдам\n\n"
            "Ботдан фойдаланиш учун сизнинг Telegram ID'ингиз админ томонидан базага қўшилган бўлиши керак.\n"
            "\"Тестни бошлаш\" тугмасини босинг ва кўрсатмага амал қилинг.\n\n"
            "Рухсат ёки саволлар бўйича админ: {admin_contact}"
        ),
    },
    "admin_commands": {
        LANG_UZ: (
            "\n\nAdmin komandalar:\n"
            "/admin - umumiy statistika\n"
            "/users - userlar ro'yxati\n"
            "/add_user TELEGRAM_ID - yangi user qo'shish\n"
            "/block_user TELEGRAM_ID - userni bloklash\n"
            "/unblock_user TELEGRAM_ID - userni qayta aktiv qilish\n"
            "/user_stats USER_ID - user statistikasi\n"
            "/seed_questions - barcha savollarni seed qilish\n"
            "/seed_districts - tuman savollarini seed qilish"
        ),
        LANG_CYRL: (
            "\n\nАдмин командалар:\n"
            "/admin - умумий статистика\n"
            "/users - userлар рўйхати\n"
            "/add_user TELEGRAM_ID - янги user қўшиш\n"
            "/block_user TELEGRAM_ID - userни блоклаш\n"
            "/unblock_user TELEGRAM_ID - userни қайта актив қилиш\n"
            "/user_stats USER_ID - user статистикаси\n"
            "/seed_questions - барча саволларни seed қилиш\n"
            "/seed_districts - туман саволларини seed қилиш"
        ),
    },
    "access_denied": {
        LANG_UZ: "Sizda botdan foydalanish uchun ruxsat yo'q.\n\nRuxsat olish uchun admin bilan bog'laning: {admin_contact}\nSizning Telegram ID: {telegram_id}",
        LANG_CYRL: "Сизда ботдан фойдаланиш учун рухсат йўқ.\n\nРухсат олиш учун админ билан боғланинг: {admin_contact}\nСизнинг Telegram ID: {telegram_id}",
    },
    "profile_title": {LANG_UZ: "Profilim", LANG_CYRL: "Профилим"},
    "last_results_title": {LANG_UZ: "Oxirgi natijalar:", LANG_CYRL: "Охирги натижалар:"},
    "no_results": {LANG_UZ: "Hozircha yakunlangan testlaringiz yo'q.", LANG_CYRL: "Ҳозирча якунланган тестларингиз йўқ."},
    "choose_direction": {LANG_UZ: "Qaysi yo'nalish bo'yicha test ishlamoqchisiz?", LANG_CYRL: "Қайси йўналиш бўйича тест ишламоқчисиз?"},
    "direction_selected": {LANG_UZ: "Yo'nalish tanlandi: {direction}\n\nNechta savoldan iborat test ishlamoqchisiz?", LANG_CYRL: "Йўналиш танланди: {direction}\n\nНечта саволдан иборат тест ишламоқчисиз?"},
    "choose_direction_first": {LANG_UZ: "Avval test yo'nalishini tanlang.", LANG_CYRL: "Аввал тест йўналишини танланг."},
    "active_test": {LANG_UZ: "Sizda aktiv test bor. Davom etamiz.", LANG_CYRL: "Сизда актив тест бор. Давом этамиз."},
    "test_started": {
        LANG_UZ: "{direction} yo'nalishi bo'yicha {total_questions} talik test boshlandi. Har bir savolga javobni ko'rsatmaga muvofiq belgilang.",
        LANG_CYRL: "{direction} йўналиши бўйича {total_questions} талик тест бошланди. Ҳар бир саволга жавобни кўрсатмага мувофиқ белгиланг.",
    },
    "cancelled": {LANG_UZ: "Test bekor qilindi.", LANG_CYRL: "Тест бекор қилинди."},
    "no_active_test": {LANG_UZ: "Sizda aktiv test yo'q.", LANG_CYRL: "Сизда актив тест йўқ."},
    "choose_menu": {LANG_UZ: "Menyudan kerakli amalni tanlang.", LANG_CYRL: "Менюдан керакли амални танланг."},
    "choose_abcd": {LANG_UZ: "Iltimos, javobni A, B, C yoki D tugmalaridan tanlang.", LANG_CYRL: "Илтимос, жавобни A, B, C ёки D тугмаларидан танланг."},
    "check_error": {LANG_UZ: "Javobni tekshirishda xatolik bo'ldi, qayta urinib ko'ring.", LANG_CYRL: "Жавобни текширишда хатолик бўлди, қайта уриниб кўринг."},
    "correct": {LANG_UZ: "To'g'ri", LANG_CYRL: "Тўғри"},
    "wrong": {LANG_UZ: "Noto'g'ri", LANG_CYRL: "Нотўғри"},
    "correct_choice": {LANG_UZ: "To'g'ri variant tanlandi.", LANG_CYRL: "Тўғри вариант танланди."},
    "correct_answer": {LANG_UZ: "To'g'ri javob: {answer}", LANG_CYRL: "Тўғри жавоб: {answer}"},
    "question_counter": {LANG_UZ: "Savol {current}/{total}", LANG_CYRL: "Савол {current}/{total}"},
    "result_title": {LANG_UZ: "Test yakunlandi!", LANG_CYRL: "Тест якунланди!"},
}


BUTTON_TEXTS = {
    "start_test": {LANG_UZ: "Testni boshlash", LANG_CYRL: "Тестни бошлаш"},
    "test_simple_mixed": {LANG_UZ: "Sodda aralash", LANG_CYRL: "Содда аралаш"},
    "test_complex_mixed": {LANG_UZ: "Murakkab aralash", LANG_CYRL: "Мураккаб аралаш"},
    "test_districts": {LANG_UZ: "Tumanlar bo'yicha", LANG_CYRL: "Туманлар бўйича"},
    "test_work_process": {LANG_UZ: "Ish jarayoni bo'yicha", LANG_CYRL: "Иш жараёни бўйича"},
    "test_30": {LANG_UZ: "30 talik test", LANG_CYRL: "30 талик тест"},
    "test_50": {LANG_UZ: "50 talik test", LANG_CYRL: "50 талик тест"},
    "last_results": {LANG_UZ: "Oxirgi natijalarim", LANG_CYRL: "Охирги натижаларим"},
    "profile": {LANG_UZ: "Profilim", LANG_CYRL: "Профилим"},
    "help": {LANG_UZ: "Yordam", LANG_CYRL: "Ёрдам"},
    "language": {LANG_UZ: "Tilni o'zgartirish", LANG_CYRL: "Тилни ўзгартириш"},
    "cancel_test": {LANG_UZ: "Testni bekor qilish", LANG_CYRL: "Тестни бекор қилиш"},
}


def normalize_language(language: str | None) -> str:
    return language if language in SUPPORTED_LANGUAGES else LANG_UZ


def text(key: str, language: str | None = LANG_UZ, **kwargs: object) -> str:
    lang = normalize_language(language)
    template = TEXTS[key][lang]
    return template.format(**kwargs)


def button(key: str, language: str | None = LANG_UZ) -> str:
    return BUTTON_TEXTS[key][normalize_language(language)]


def button_values(key: str) -> set[str]:
    return set(BUTTON_TEXTS[key].values())


PROTECTED_TERMS = (
    "MeaSoft App",
    "LIFE PAY",
    "EMU Express",
    "IKPU",
    "EMU TEST BOT",
    "EMU",
    "Google отзыв",
    "Telegram",
    "SQLite",
    "OpenAI",
    "JSON",
    "API",
    "ID",
    "QR",
    "manifest",
    "Manifest",
    "MANIFEST",
    "kuryer",
    "kuryerlik",
    "online",
    "onlayn",
    "login",
    "parol",
    "zakaz",
    "Адрес",
    "Адреса",
    "Адресное хранение",
    "Вложения",
    "Выдача",
    "Доска приёма",
    "Доска приема",
    "Манифест",
    "Сборка комплектов",
    "Справочники",
    "Фильтр",
    "Функции",
    "получен",
    "переместить в доставку",
)


_MULTI_CHAR_MAP = {
    "o'": "ў",
    "o‘": "ў",
    "o`": "ў",
    "g'": "ғ",
    "g‘": "ғ",
    "g`": "ғ",
    "sh": "ш",
    "ch": "ч",
    "yo": "ё",
    "yu": "ю",
    "ya": "я",
    "ye": "е",
    "ksiya": "кция",
    "iya": "ия",
    "ts": "ц",
    "iy": "ий",
}

_CHAR_MAP = {
    "a": "а",
    "b": "б",
    "d": "д",
    "e": "е",
    "f": "ф",
    "g": "г",
    "h": "ҳ",
    "i": "и",
    "j": "ж",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "q": "қ",
    "r": "р",
    "s": "с",
    "t": "т",
    "u": "у",
    "v": "в",
    "x": "х",
    "y": "й",
    "z": "з",
    "'": "ъ",
    "‘": "ъ",
    "`": "ъ",
}


def _match_case(source: str, target: str) -> str:
    if source.isupper():
        return target.upper()
    if source[:1].isupper():
        return target[:1].upper() + target[1:]
    return target


def latin_to_cyrillic(value: str) -> str:
    result: list[str] = []
    i = 0
    while i < len(value):
        matched = False
        for size in (5, 4, 3, 2):
            chunk = value[i : i + size]
            lower = chunk.lower()
            if lower == "iye":
                result.append(_match_case(chunk, "ие"))
                i += size
                matched = True
                break
            if lower in _MULTI_CHAR_MAP:
                result.append(_match_case(chunk, _MULTI_CHAR_MAP[lower]))
                i += size
                matched = True
                break
        if matched:
            continue

        chunk2 = value[i : i + 2]
        lower2 = chunk2.lower()
        if lower2 in _MULTI_CHAR_MAP:
            result.append(_match_case(chunk2, _MULTI_CHAR_MAP[lower2]))
            i += 2
            continue

        char = value[i]
        mapped = _CHAR_MAP.get(char.lower())
        result.append(_match_case(char, mapped) if mapped else char)
        i += 1
    return "".join(result)


def _protect_terms(value: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}
    result = value
    for index, term in enumerate(sorted(PROTECTED_TERMS, key=len, reverse=True)):
        if term not in result:
            continue
        placeholder = f"\uE000{index}\uE001"
        protected[placeholder] = term
        result = result.replace(term, placeholder)
    return result, protected


def _restore_terms(value: str, protected: dict[str, str]) -> str:
    result = value
    for placeholder, term in protected.items():
        result = result.replace(placeholder, term)
    return result


def localize_value(value: str, language: str | None = LANG_UZ) -> str:
    if normalize_language(language) == LANG_CYRL:
        protected_value, protected = _protect_terms(value)
        return _restore_terms(latin_to_cyrillic(protected_value), protected)
    return value
