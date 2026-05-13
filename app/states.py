from aiogram.fsm.state import State, StatesGroup


class TestStates(StatesGroup):
    answering = State()
