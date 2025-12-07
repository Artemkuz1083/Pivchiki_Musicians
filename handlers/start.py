from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from database.queries import check_user, get_band_data_by_user_id, check_exist_band
from states.states_registration import RegistrationStates

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "no_username"
    logger.info("Пользователь ID=%s (@%s) вызвал /start", user_id, username)

    try:
        exist = await check_user(user_id)
    except Exception:
        logger.exception("Ошибка при проверке пользователя %s в БД", user_id)
        await message.answer("Произошла ошибка. Попробуйте позже.")
        return

    if exist:
        logger.info("Пользователь %s уже зарегистрирован", user_id)

        # 1. Проверяем наличие группы
        band_exists = False
        try:
            band_exists = await check_exist_band(user_id)
        except Exception:
            logger.exception("Ошибка при проверке группы пользователя %s в БД", user_id)
            # В случае ошибки лучше считать, что группа есть, чтобы не предложить регистрацию повторно
            band_exists = True

        kb = [
            [types.KeyboardButton(text="👤 Моя анкета")],
            [types.KeyboardButton(text="🔍 Смотреть анкеты")],
        ]

        # 2. Условное добавление кнопки "Зарегистрировать группу"
        if not band_exists:
            kb.append([types.KeyboardButton(text="🎸 Зарегистрировать группу")])
        else:
            kb.append([types.KeyboardButton(text="🎸 Моя группа")])  # Эта кнопка всегда должна быть в конце


        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(text="Привет, Родной", reply_markup=keyboard)
    else:
        logger.info("Пользователь %s — новый, отправляем на регистрацию", user_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data="start_registration"))
        keyboard.add(InlineKeyboardButton(text="Смотреть анкеты", callback_data="show_without_registration"))
        await message.answer(
            text="Привет, рады тебя приветствовать в нашем боте для поиска музыкантов. Ты можешь приступить сразу к просмотру анкет, но без возможности ставить лайки",
            reply_markup=keyboard.as_markup())