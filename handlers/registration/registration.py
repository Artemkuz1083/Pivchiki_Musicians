from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from states.states_registration import RegistrationStates

router = Router()

@router.message(F.text.endswith("Let's go"))
async def start_search(message: types.Message, state: FSMContext):

    await state.set_state(RegistrationStates.name)
    await message.answer("Начнем с базовых вопросов. "
                         "После вы можете расширить информацию в профиле "
                         "Введите ваше имя: ")

@router.message(F.text, RegistrationStates.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text

    await state.update_data(name=name)
    await message.answer("Введите ваш город:")
    await state.set_state(RegistrationStates.city)

def make_keyboard_for_instruments(selected):
    instruments = ["Гитара", "Барабаны", "Синтезатор", "Вокал", "Бас", "Скрипка", "Свой вариант"]

    buttons = []
    for inst in instruments:
        text = f"✅ {inst}" if inst in selected else inst
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"inst_{inst}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text, RegistrationStates.city)
async def get_city(message: types.Message, state: FSMContext):
    city = message.text.lower()
    await state.update_data(city=city)

    msg_text = "Выберите инструмент/инструменты, которыми вы владеете:"
    markup = make_keyboard_for_instruments([])

    await message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.instrument)
    await state.update_data(user_choice_inst=[])
    await state.update_data(own_user_inst=[])


@router.callback_query(F.data.startswith("inst_"), RegistrationStates.instrument)
async def choose_instrument(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_inst", [])

    if choose == "Свой вариант":
        await callback.message.edit_text(text="Напишите инструмент:")
        await state.set_state(RegistrationStates.own_instrument)
        return
    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_instruments(user_choice)
    )
    await state.update_data(user_choice_inst=user_choice)
    await callback.answer()

@router.message(F.text, RegistrationStates.own_instrument)
async def own_instrument(message: types.Message, state: FSMContext):
    inst = message.text
    data = await state.get_data()
    user_inst = data.get("own_user_inst", [])
    user_choice = data.get("user_choice_inst", [])
    user_inst.append(inst)
    msg_text = (f"Свой вариант:{user_inst}\n"
                "Выберите инструмент/инструменты, которыми вы владеете:")
    await message.answer(text=msg_text, reply_markup=make_keyboard_for_instruments(user_choice))
    await state.set_state(RegistrationStates.instrument)


@router.callback_query(F.data.startswith("done"), RegistrationStates.instrument)
async def done(callback: types.CallbackQuery, state: FSMContext):

    msg_text = "Отлично! Теперь выберите жанры в которых вы играете:"
    markup = make_keyboard_for_genre([])
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.genre)
    await state.update_data(user_choice_genre= [])
    await state.update_data(own_user_genre=[])

def make_keyboard_for_genre(selected):
    genres = ["Рок", "Поп рок", "Гранж", "Метал", "Ню метал", "Панк", "Свой вариант"]

    buttons = []
    for genre in genres:
        text = f"✅ {genre}" if genre in selected else genre
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"genre_{genre}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("genre_"), RegistrationStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        await callback.message.edit_text(text="Напишите жанр:")
        await state.set_state(RegistrationStates.own_genre)
        return
    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_genre(user_choice)
    )
    await state.update_data(user_choice_genre=user_choice)
    await callback.answer()

@router.message(F.text, RegistrationStates.own_genre)
async def own_instrument(message: types.Message, state: FSMContext):
    inst = message.text
    data = await state.get_data()
    user_inst = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])
    user_inst.append(inst)
    msg_text = (f"Свой вариант:{user_inst}\n"
                "Отлично! Теперь выберите жанры в которых вы играете:")
    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice))
    await state.set_state(RegistrationStates.genre)

@router.callback_query(F.data.startswith("done"), RegistrationStates.genre)
async def done(callback: types.CallbackQuery, state: FSMContext):
    msg_text = "Отлично! Теперь вам доступен ваш профиль. Для того что ваше объявление привлекло больше внимания, мы советуем вам дополнить информацию в нем."
    button = [
        [types.InlineKeyboardButton(text="Моя анкета", callback_data="my_profile")],
        [types.InlineKeyboardButton(text="Смотреть анкеты", callback_data="search")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=button)
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await state.clear()



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

@router.callback_query(F.data.startswith("practice_") , RegistrationStates.level_practice)
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