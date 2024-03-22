from aiogram.fsm.state import State, StatesGroup


class AddNewInformation(StatesGroup):
    information = State()
