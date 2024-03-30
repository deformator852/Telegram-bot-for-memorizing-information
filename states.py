from aiogram.fsm.state import State, StatesGroup


class AddNewInformation(StatesGroup):
    INFORMATION = State()


class SendMessageToSupport(StatesGroup):
    MESSAGE = State()
