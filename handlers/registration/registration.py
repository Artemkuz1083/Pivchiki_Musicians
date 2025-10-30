from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sources.postgres import sql

from states.states_registration import RegistrationStates

router = Router()

@router.message(F.text.endswith("Let's go"))
async def start_search(message: types.Message, state: FSMContext):

    await message.answer("Введите ваше имя:")
    await state.set_state(RegistrationStates.name)


@router.message(F.text, RegistrationStates.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text

    await state.update_data(name=name)
    await message.answer("Введите ваш возраст:")
    await state.set_state(RegistrationStates.age)


@router.message(F.text, RegistrationStates.age)
async def get_age(message: types.Message, state: FSMContext):
    age = message.text

    if not age.isdigit():
        await message.answer("Пожалуйста, введите число (ваш возраст цифрами):")
        return

    await state.update_data(age=age)
    markup = InlineKeyboardBuilder()
    _one = types.InlineKeyboardButton(
        text="⭐️",
        callback_data="practice_1"
    )
    _two = types.InlineKeyboardButton(
        text="⭐️⭐️",
        callback_data="practice_2"
    )
    _three = types.InlineKeyboardButton(
        text="⭐️️⭐️️⭐️️",
        callback_data="practice_3"
    )
    _four = types.InlineKeyboardButton(
        text="⭐️⭐️⭐️⭐️️️",
        callback_data="practice_4"
    )
    _five = types.InlineKeyboardButton(
        text="⭐⭐️️⭐️️⭐️️⭐️️️",
        callback_data="practice_5"
    )
    markup.add(_one, _two, _three, _four, _five)
    markup.adjust(1, 1)
    await state.set_state(RegistrationStates.level_practice)
    await message.answer()

@router.callback_query(F.data.startswith == "practice_" , RegistrationStates.level_practice)
async def get_level_practice(callback: types.CallbackQuery, state: FSMContext):
    practice_level = int(callback.data.split("_")[1])


    await state.update_data(practice_level=practice_level)
    markup = InlineKeyboardBuilder()
    _one = types.InlineKeyboardButton(
        text="⭐️",
        callback_data="practice_1"
    )
    _two = types.InlineKeyboardButton(
        text="⭐️⭐️",
        callback_data="practice_2"
    )
    _three = types.InlineKeyboardButton(
        text="⭐️️⭐️️⭐️️",
        callback_data="practice_3"
    )
    _four = types.InlineKeyboardButton(
        text="⭐️⭐️⭐️⭐️️️",
        callback_data="practice_4"
    )
    _five = types.InlineKeyboardButton(
        text="⭐⭐️️⭐️️⭐️️⭐️️️",
        callback_data="practice_5"
    )
    markup.add(_one, _two, _three, _four, _five)
    markup.adjust(1, 1)
    await state.set_state(RegistrationStates.level_theoretical)