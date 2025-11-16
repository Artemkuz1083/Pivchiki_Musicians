from aiogram.fsm.state import StatesGroup, State


class BandRegistrationStates(StatesGroup):
    """Состояния для регистрации музыкальной группы."""

    filling_name = State()
    filling_foundation_date = State()
    selecting_genres = State()
    filling_own_genre = State()