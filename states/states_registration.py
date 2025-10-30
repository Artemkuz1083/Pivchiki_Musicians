from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    name = State()
    age = State()
    city = State()
    level_practice = State()
    level_theoretical = State()
    genre = State()
    own_genre = State()

