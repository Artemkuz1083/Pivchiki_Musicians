from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    start_registration = State()
    name = State()
    age = State()
    city = State()
    own_city = State()
    msg_about_city = State()
    instrument = State()
    own_instrument = State()
    level_practice = State()
    level_theoretical = State()
    genre = State()
    own_genre = State()
    contacts = State()
    finish = State()

