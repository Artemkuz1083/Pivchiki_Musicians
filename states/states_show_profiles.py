from aiogram.fsm.state import State, StatesGroup

class ShowProfiles(StatesGroup):
    choose = State()
    show_profiles = State()
    show_bands = State()
