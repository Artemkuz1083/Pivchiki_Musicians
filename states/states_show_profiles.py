from aiogram.fsm.state import State, StatesGroup

class ShowProfiles(StatesGroup):
    choose = State()
    show_profiles = State()
    show_bands = State()
    filter_menu = State()  # Основное меню фильтров
    filter_city = State()
    filter_genres = State()
    filter_level = State()
