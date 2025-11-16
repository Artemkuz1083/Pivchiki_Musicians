from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from database.queries import check_user
from states.states_registration import RegistrationStates

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "no_username"
    logger.info("Пользователь ID=%s (@%s) вызвал /start", user_id, username)

    try:
        exist = await check_user(user_id)
    except Exception:
        logger.exception("Ошибка при проверке пользователя %s в БД", user_id)
        await message.answer("Произошла ошибка. Попробуйте позже.")
        return

    #TODO просмотр анкеты и там лайков, сообщений
    if exist:
        logger.info("Пользователь %s уже зарегистрирован", user_id)
        kb = [
            [types.KeyboardButton(text="Моя анкета")],
            [types.KeyboardButton(text="Что-то ещё")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(text="Привет, Родной", reply_markup=keyboard)
    else:
        logger.info("Пользователь %s — новый, отправляем на регистрацию", user_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Let's go", callback_data="start_registration"))
        await message.answer(text="Привет, рады тебя приветствовать в нашем боте для поиска музыкантов. Но прежде чем ты приступишь к поиску надо пройти регистрацию", reply_markup=keyboard.as_markup())
        await state.set_state(RegistrationStates.start_registration)