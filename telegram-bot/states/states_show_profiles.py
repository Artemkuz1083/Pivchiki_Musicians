from aiogram.fsm.state import State, StatesGroup

class ShowProfiles(StatesGroup):
    choose = State()
    show_profiles = State()
    show_bands = State()
    filter_menu = State()  # Основное меню фильтров
    filter_city = State()
    filter_city_custom = State()
    filter_instruments = State()
    filter_instruments_custom = State()
    filter_genres = State()
    filter_genres_custom = State()
    filter_experience = State()
    filter_level = State()
    filter_group_level = State()
    filter_group_city = State()
    filter_group_genres = State()
    filter_group_genres_custom = State()
    filter_group_menu = State()
