from aiogram.fsm.state import State, StatesGroup

class BandEditingStates(StatesGroup):
    editing_band_name = State()
    editing_band_year = State()
    editing_genres = State()
    inputting_own_genre = State()