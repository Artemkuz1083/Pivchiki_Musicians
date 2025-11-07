from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    name = State()
    age = State()
    city = State()
    instrument = State()
    own_instrument = State()
    level_practice = State()
    level_theoretical = State()
    genre = State()
    own_genre = State()
    finish = State()

