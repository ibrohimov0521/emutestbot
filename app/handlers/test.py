from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.keyboards import (
    BTN_CANCEL_TEST,
    BTN_START_TEST,
    BTN_TEST_DISTRICTS,
    BTN_TEST_MANUAL,
    BTN_TEST_MIXED,
    BTN_TEST_30,
    BTN_TEST_50,
    choice_answer_menu,
    main_menu,
    test_menu,
    test_direction_menu,
    test_size_menu,
)
from app.services import test_service, user_service
from app.services.openai_checker import AnswerCheckError, OpenAIAnswerChecker

router = Router()
checker: OpenAIAnswerChecker | None = None
pending_test_directions: dict[int, str] = {}

TEST_DIRECTION_LABELS = {
    test_service.TEST_DIRECTION_DISTRICTS: "Tumanlar bo'yicha",
    test_service.TEST_DIRECTION_MANUAL: "Ichki nizom va dastur bo'yicha",
    test_service.TEST_DIRECTION_MIXED: "Aralash",
}


def get_checker() -> OpenAIAnswerChecker:
    global checker
    if checker is None:
        checker = OpenAIAnswerChecker()
    return checker


async def _ensure_allowed(message: Message) -> int | None:
    if not message.from_user:
        return None
    try:
        return await user_service.upsert_user(message.from_user)
    except PermissionError:
        await message.answer(user_service.access_denied_text(message.from_user.id))
        return None


async def _send_next_question(message: Message, session_id: int) -> None:
    session = await test_service.get_session(session_id)
    question = await test_service.get_next_question(session_id)
    if not question:
        if session:
            if session["status"] == "active":
                await test_service.finish_session(session_id)
                session = await test_service.get_session(session_id)
            if session:
                await message.answer(test_service.format_result(session), reply_markup=main_menu())
        return
    answered = await test_service.count_answered(session_id)
    total_questions = int(session["total_questions"]) if session else 50
    reply_markup = choice_answer_menu() if test_service.is_choice_question(question) else test_menu()
    await message.answer(test_service.format_question_text(question, answered, total_questions), reply_markup=reply_markup)


@router.message(F.text == BTN_START_TEST)
async def start_test(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "start_test")
    active = await test_service.get_active_session(user_id)
    if active:
        await message.answer("Sizda aktiv test bor. Davom etamiz.", reply_markup=test_menu())
        await _send_next_question(message, active["id"])
        return

    pending_test_directions.pop(message.from_user.id, None)
    await message.answer("Qaysi yo'nalish bo'yicha test ishlamoqchisiz?", reply_markup=test_direction_menu())


@router.message(F.text.in_({BTN_TEST_DISTRICTS, BTN_TEST_MANUAL, BTN_TEST_MIXED}))
async def choose_test_direction(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    direction_by_button = {
        BTN_TEST_DISTRICTS: test_service.TEST_DIRECTION_DISTRICTS,
        BTN_TEST_MANUAL: test_service.TEST_DIRECTION_MANUAL,
        BTN_TEST_MIXED: test_service.TEST_DIRECTION_MIXED,
    }
    direction = direction_by_button[message.text]
    pending_test_directions[message.from_user.id] = direction
    await user_service.log_operation(user_id, "choose_test_direction", {"direction": direction})
    await message.answer(
        f"Yo'nalish tanlandi: {TEST_DIRECTION_LABELS[direction]}\n\n"
        "Nechta savoldan iborat test ishlamoqchisiz?",
        reply_markup=test_size_menu(),
    )


@router.message(F.text.in_({BTN_TEST_30, BTN_TEST_50}))
async def choose_test_size(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    direction = pending_test_directions.get(message.from_user.id)
    if direction is None:
        await message.answer("Avval test yo'nalishini tanlang.", reply_markup=test_direction_menu())
        return
    total_questions = 30 if message.text == BTN_TEST_30 else 50
    await user_service.log_operation(
        user_id,
        "choose_test_size",
        {"total_questions": total_questions, "direction": direction},
    )
    active = await test_service.get_active_session(user_id)
    if active:
        await message.answer("Sizda aktiv test bor. Davom etamiz.", reply_markup=test_menu())
        await _send_next_question(message, active["id"])
        return

    try:
        session = await test_service.start_test(user_id, total_questions, direction)
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=main_menu())
        return

    pending_test_directions.pop(message.from_user.id, None)
    await message.answer(
        f"{TEST_DIRECTION_LABELS[direction]} yo'nalishi bo'yicha {total_questions} talik test boshlandi. "
        "Har bir savolga javobni matn ko'rinishida yozing.",
        reply_markup=test_menu(),
    )
    await _send_next_question(message, session["id"])


@router.message(F.text == BTN_CANCEL_TEST)
async def cancel_test(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "cancel_test")
    pending_test_directions.pop(message.from_user.id, None)
    cancelled = await test_service.cancel_active_session(user_id)
    text = "Test bekor qilindi." if cancelled else "Sizda aktiv test yo'q."
    await message.answer(text, reply_markup=main_menu())


@router.message(F.text & ~F.text.startswith("/"))
async def answer_question(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    active = await test_service.get_active_session(user_id)
    if not active:
        await message.answer("Menyudan kerakli amalni tanlang.", reply_markup=main_menu())
        return

    question = await test_service.get_next_question(active["id"])
    if not question:
        session = await test_service.get_session(active["id"])
        if session:
            await message.answer(test_service.format_result(session), reply_markup=main_menu())
        return

    await user_service.log_operation(user_id, "answer_question", {"question_id": question["id"]})
    user_answer = message.text
    if test_service.is_choice_question(question):
        result = test_service.check_choice_answer(question, message.text)
        if result is None:
            await message.answer("Iltimos, javobni A, B, C yoki D tugmalaridan tanlang.", reply_markup=choice_answer_menu())
            return
        user_answer = test_service.format_choice_user_answer(question, message.text)
    else:
        try:
            result = await get_checker().check(question["question_text"], question["correct_answer"], message.text)
        except AnswerCheckError:
            await message.answer("Javobni tekshirishda xatolik bo'ldi, qayta urinib ko'ring.", reply_markup=test_menu())
            return

    session = await test_service.save_answer(active["id"], question, user_answer, result)
    mark = "To'g'ri" if result.is_correct else "Noto'g'ri"
    await message.answer(f"{mark}. {result.reason}")

    if session.get("status") == "finished":
        await message.answer(test_service.format_result(session), reply_markup=main_menu())
    else:
        await _send_next_question(message, active["id"])
