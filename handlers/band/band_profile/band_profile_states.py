from aiogram.fsm.state import State, StatesGroup

class BandEditingStates(StatesGroup):
    editing_band_name = State()
    editing_band_year = State()
    editing_genres = State()
    inputting_own_genre = State()
    editing_city = State()
    inputting_own_city = State()
    editing_description = State()
    editing_seriousness_level = State()