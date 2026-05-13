from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.keyboards import (
    BTN_CANCEL_TEST,
    BTN_START_TEST,
    BTN_TEST_30,
    BTN_TEST_50,
    main_menu,
    test_menu,
    test_size_menu,
)
from app.services import test_service, user_service
from app.services.openai_checker import AnswerCheckError, OpenAIAnswerChecker

router = Router()
checker: OpenAIAnswerChecker | None = None


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
    await message.answer(
        f"Savol {answered + 1}/{session['total_questions'] if session else 50}\n\n{question['question_text']}",
        reply_markup=test_menu(),
    )


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

    await message.answer("Nechta savoldan iborat test ishlamoqchisiz?", reply_markup=test_size_menu())


@router.message(F.text.in_({BTN_TEST_30, BTN_TEST_50}))
async def choose_test_size(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    total_questions = 30 if message.text == BTN_TEST_30 else 50
    await user_service.log_operation(user_id, "choose_test_size", {"total_questions": total_questions})
    active = await test_service.get_active_session(user_id)
    if active:
        await message.answer("Sizda aktiv test bor. Davom etamiz.", reply_markup=test_menu())
        await _send_next_question(message, active["id"])
        return

    try:
        session = await test_service.start_test(user_id, total_questions)
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=main_menu())
        return

    await message.answer(
        f"{total_questions} talik test boshlandi. Har bir savolga javobni matn ko'rinishida yozing.",
        reply_markup=test_menu(),
    )
    await _send_next_question(message, session["id"])


@router.message(F.text == BTN_CANCEL_TEST)
async def cancel_test(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    await user_service.log_operation(user_id, "cancel_test")
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
    try:
        result = await get_checker().check(question["question_text"], question["correct_answer"], message.text)
    except AnswerCheckError:
        await message.answer("Javobni tekshirishda xatolik bo'ldi, qayta urinib ko'ring.", reply_markup=test_menu())
        return

    session = await test_service.save_answer(active["id"], question, message.text, result)
    mark = "To'g'ri" if result.is_correct else "Noto'g'ri"
    await message.answer(f"{mark}. {result.reason}")

    if session.get("status") == "finished":
        await message.answer(test_service.format_result(session), reply_markup=main_menu())
    else:
        await _send_next_question(message, active["id"])
