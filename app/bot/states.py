from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    choosing_document = State()
    deleting_document = State()
