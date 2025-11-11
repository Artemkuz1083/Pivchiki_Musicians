from aiogram import types, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.queries import check_user
from states.states_registration import RegistrationStates

router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    exist = await check_user(user_id)
    #TODO просмотр анкеты и там лайков, сообщений
    if exist:
        kb = [
            [types.KeyboardButton(text="Моя анкета")],
            [types.KeyboardButton(text="Что-то ещё")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

        await message.answer(text="Привет, Родной", reply_markup=keyboard)

    if not exist:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Let's go", callback_data="start_registration"))
        await message.answer(text="Привет, рады тебя приветствовать в нашем боте для поиска музыкантов. Но прежде чем ты приступишь к поиску надо пройти регистрацию", reply_markup=keyboard.as_markup())
        await state.set_state(RegistrationStates.start_registration)