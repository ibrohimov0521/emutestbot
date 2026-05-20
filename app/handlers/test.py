from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.keyboards import (
    choice_answer_menu,
    main_menu,
    test_menu,
    test_direction_menu,
    test_size_menu,
)
from app.i18n import button, button_values, text
from app.services import test_service, user_service
from app.services.openai_checker import AnswerCheckError, OpenAIAnswerChecker

router = Router()
checker: OpenAIAnswerChecker | None = None
pending_test_directions: dict[int, str] = {}

TEST_DIRECTION_LABELS = {
    test_service.TEST_DIRECTION_DISTRICTS: "test_districts",
    test_service.TEST_DIRECTION_MANUAL: "test_manual",
    test_service.TEST_DIRECTION_MIXED: "test_mixed",
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
    language = "uz"
    if session:
        language = await user_service.get_language(int(session["user_id"]))
    question = await test_service.get_next_question(session_id)
    if not question:
        if session:
            if session["status"] == "active":
                await test_service.finish_session(session_id)
                session = await test_service.get_session(session_id)
            if session:
                await message.answer(test_service.format_result(session, language), reply_markup=main_menu(language))
        return
    answered = await test_service.count_answered(session_id)
    total_questions = int(session["total_questions"]) if session else 50
    reply_markup = choice_answer_menu(language) if test_service.is_choice_question(question) else test_menu(language)
    await message.answer(
        test_service.format_question_text(question, answered, total_questions, language),
        reply_markup=reply_markup,
    )


@router.message(F.text.in_(button_values("start_test")))
async def start_test(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    await user_service.log_operation(user_id, "start_test")
    active = await test_service.get_active_session(user_id)
    if active:
        await message.answer(text("active_test", language), reply_markup=test_menu(language))
        await _send_next_question(message, active["id"])
        return

    pending_test_directions.pop(message.from_user.id, None)
    await message.answer(text("choose_direction", language), reply_markup=test_direction_menu(language))


@router.message(F.text.in_(button_values("test_districts") | button_values("test_manual") | button_values("test_mixed")))
async def choose_test_direction(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    direction_by_button = {
        button("test_districts", "uz"): test_service.TEST_DIRECTION_DISTRICTS,
        button("test_districts", "cyrl"): test_service.TEST_DIRECTION_DISTRICTS,
        button("test_manual", "uz"): test_service.TEST_DIRECTION_MANUAL,
        button("test_manual", "cyrl"): test_service.TEST_DIRECTION_MANUAL,
        button("test_mixed", "uz"): test_service.TEST_DIRECTION_MIXED,
        button("test_mixed", "cyrl"): test_service.TEST_DIRECTION_MIXED,
    }
    direction = direction_by_button[message.text]
    pending_test_directions[message.from_user.id] = direction
    await user_service.log_operation(user_id, "choose_test_direction", {"direction": direction})
    await message.answer(
        text("direction_selected", language, direction=button(TEST_DIRECTION_LABELS[direction], language)),
        reply_markup=test_size_menu(language),
    )


@router.message(F.text.in_(button_values("test_30") | button_values("test_50")))
async def choose_test_size(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    direction = pending_test_directions.get(message.from_user.id)
    if direction is None:
        await message.answer(text("choose_direction_first", language), reply_markup=test_direction_menu(language))
        return
    total_questions = 30 if message.text in button_values("test_30") else 50
    await user_service.log_operation(
        user_id,
        "choose_test_size",
        {"total_questions": total_questions, "direction": direction},
    )
    active = await test_service.get_active_session(user_id)
    if active:
        await message.answer(text("active_test", language), reply_markup=test_menu(language))
        await _send_next_question(message, active["id"])
        return

    try:
        session = await test_service.start_test(user_id, total_questions, direction)
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=main_menu(language))
        return

    pending_test_directions.pop(message.from_user.id, None)
    await message.answer(
        text(
            "test_started",
            language,
            direction=button(TEST_DIRECTION_LABELS[direction], language),
            total_questions=total_questions,
        ),
        reply_markup=test_menu(language),
    )
    await _send_next_question(message, session["id"])


@router.message(F.text.in_(button_values("cancel_test")))
async def cancel_test(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    await user_service.log_operation(user_id, "cancel_test")
    pending_test_directions.pop(message.from_user.id, None)
    cancelled = await test_service.cancel_active_session(user_id)
    message_text = text("cancelled", language) if cancelled else text("no_active_test", language)
    await message.answer(message_text, reply_markup=main_menu(language))


@router.message(F.text & ~F.text.startswith("/"))
async def answer_question(message: Message) -> None:
    user_id = await _ensure_allowed(message)
    if user_id is None:
        return
    language = await user_service.get_language(user_id)
    active = await test_service.get_active_session(user_id)
    if not active:
        await message.answer(text("choose_menu", language), reply_markup=main_menu(language))
        return

    question = await test_service.get_next_question(active["id"])
    if not question:
        session = await test_service.get_session(active["id"])
        if session:
            await message.answer(test_service.format_result(session, language), reply_markup=main_menu(language))
        return

    await user_service.log_operation(user_id, "answer_question", {"question_id": question["id"]})
    user_answer = message.text
    if test_service.is_choice_question(question):
        result = test_service.check_choice_answer(question, message.text, language)
        if result is None:
            await message.answer(text("choose_abcd", language), reply_markup=choice_answer_menu(language))
            return
        user_answer = test_service.format_choice_user_answer(question, message.text)
    else:
        try:
            result = await get_checker().check(
                test_service.display_text(question["question_text"], language),
                test_service.display_text(question["correct_answer"], language),
                message.text,
            )
        except AnswerCheckError:
            await message.answer(text("check_error", language), reply_markup=test_menu(language))
            return

    session = await test_service.save_answer(active["id"], question, user_answer, result)
    if not result.is_correct and test_service.is_district_region_question(question):
        if test_service.is_known_region_answer(message.text):
            await message.answer(test_service.format_district_wrong_answer(question, language))
        else:
            await message.answer(test_service.format_unknown_region_answer(language))
    else:
        mark = text("correct", language) if result.is_correct else text("wrong", language)
        await message.answer(f"{mark}. {result.reason}")

    if session.get("status") == "finished":
        await message.answer(test_service.format_result(session, language), reply_markup=main_menu(language))
    else:
        await _send_next_question(message, active["id"])
