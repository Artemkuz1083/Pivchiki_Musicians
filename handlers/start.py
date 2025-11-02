from aiogram import types, Router
from aiogram.filters import Command
from database.queries import check_user


router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
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

        #TODO регистрация
        kb = [
            [types.KeyboardButton(text="Let's go")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

        await message.answer(text="Привет, рады тебя приветствовать в нашем боте для поиска музыкантов. Но прежде чем ты приступишь к поиску надо пройти регистрацию", reply_markup=keyboard)