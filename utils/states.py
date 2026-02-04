from aiogram.fsm.state import State, StatesGroup

class GenStates(StatesGroup):
    waiting_for_photo = State()
    adjusting_settings = State()