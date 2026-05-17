from aiogram.fsm.state import State, StatesGroup


class TestStates(StatesGroup):
    answering = State()


class AdminStates(StatesGroup):
    waiting_add_user_id = State()
    waiting_block_user_id = State()
    waiting_unblock_user_id = State()
    waiting_user_stats_id = State()
