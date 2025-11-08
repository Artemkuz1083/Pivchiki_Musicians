from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):

    select_param_to_fill = State()
    filling_age = State()
    select_instrument_to_edit = State()
    filling_level = State()
    selecting_theory_level = State()
    selecting_experience_type = State()
    filling_experience_description = State()
    filling_theory = State()
    uploading_files = State()
    uploading_profile_photo = State()
    filling_external_link = State()