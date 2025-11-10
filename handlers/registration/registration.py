from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from database.models import *

from database.queries import *
from states.states_registration import RegistrationStates

router = Router()

@router.message(F.text.endswith("Let's go") | F.text.endswith("Создать анкету"))
async def start_search(message: types.Message, state: FSMContext):

    await state.set_state(RegistrationStates.name)
    await message.answer("Начнем с базовых вопросов. "
                         "После вы можете расширить информацию в профиле "
                         "Введите ваше имя: ")

@router.message(F.text, RegistrationStates.name)
async def get_name(message: types.Message, state: FSMContext):
    """Получаем имя от пользователя"""
    name = message.text
    user_id = message.from_user.id

    try:
        await create_user(user_id=user_id)
        await update_user_name(user_id, name)
    except Exception as e:
        logger.error(f"Ошибка при записи данных пользователя: {e}")
        return

    await state.update_data(user_id=user_id)
    await state.update_data(name=name)
    await message.answer("Введите ваш город:")
    await state.set_state(RegistrationStates.city)

def make_keyboard_for_instruments(selected):
    """Клавиатура для инструментов"""
    instruments = ["Гитара", "Барабаны", "Синтезатор", "Вокал", "Бас", "Скрипка", "Свой вариант"]

    buttons = []
    for inst in instruments:
        text = f"✅ {inst}" if inst in selected else inst
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"inst_{inst}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text, RegistrationStates.city)
async def get_city(message: types.Message, state: FSMContext):
    """Получаем город"""
    city = message.text.lower()
    await state.update_data(city=city)

    data = await state.get_data()
    user_id = data.get("user_id")

    try:
       await update_user_city(user_id, city)
    except Exception as e:
        logger.error(f"Ошибка при записи данных пользователя: {e}")
        return

    msg_text = "Выберите инструмент/инструменты, которыми вы владеете:"
    markup = make_keyboard_for_instruments([])

    await message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.instrument)
    await state.update_data(user_choice_inst=[])
    await state.update_data(own_user_inst=[])


@router.callback_query(F.data.startswith("inst_"), RegistrationStates.instrument)
async def choose_instrument(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для инструментов"""
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
    """Обработка кнопки свой вариант для инструментов"""
    inst = message.text
    data = await state.get_data()
    user_inst = data.get("own_user_inst", [])
    user_choice = data.get("user_choice_inst", [])
    user_inst.append(inst)
    msg_text = (f"Свой вариант:{user_inst}\n"
                "Выберите инструмент/инструменты, которыми вы владеете:")
    await message.answer(text=msg_text, reply_markup=make_keyboard_for_instruments(user_choice))
    await state.set_state(RegistrationStates.instrument)


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # можно поменять на DEBUG для подробных логов
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("done"), RegistrationStates.instrument)
async def done(callback: types.CallbackQuery, state: FSMContext):
    from handlers.profile.profile import get_instrument_selection_keyboard
    """Обработка кнопки готово для инструментов"""
    msg_text = "Выберите инструмент который вы хотите оценить:"
    data = await state.get_data()

    logger.info("FSM data: %s", data)

    user_choice_inst = data.get("user_choice_inst", [])
    own_user_inst = data.get("own_user_inst", [])
    user_id = data.get("user_id")

    logger.info("user_choice_inst: %s", user_choice_inst)
    logger.info("own_user_inst: %s", own_user_inst)
    logger.info("user_id: %s", user_id)

    all_user_inst = user_choice_inst + own_user_inst
    instruments_list = [Instrument(name=inst, proficiency_level=0) for inst in all_user_inst]

    logger.info("instruments_list для БД: %s", instruments_list)

    try:
        await update_user_instruments(user_id=user_id, instruments=instruments_list)
        logger.info("Инструменты успешно обновлены в БД")
    except Exception as e:
        logger.error("Ошибка при добавлении инструмента в БД: %s", e)
        return

    try:
        markup = get_instrument_selection_keyboard(instruments_list)
        await callback.message.answer(text=msg_text, reply_markup=markup)
        logger.info("Клавиатура инструментов успешно отправлена")
    except Exception as e:
        logger.error("Ошибка при создании или отправке клавиатуры: %s", e)
        return

    try:
        await state.set_state(RegistrationStates.level_practice)
        await state.update_data(instruments_list=instruments_list)
        logger.info("FSM состояние обновлено на level_practice")
    except Exception as e:
        logger.error("Ошибка при обновлении состояния FSM: %s", e)

def keyboard_rating_practice(inst_id: int):
    markup = InlineKeyboardBuilder()

    for i in range(1, 6):
        stars ="⭐️" * i
        button = InlineKeyboardButton(
            text=f"{i} stars",
            callback_data=f"practice_{i}_{inst_id}"
        )
        markup.add(button)

    markup.adjust(5)

    return markup


def get_instrument_rating(instruments: list) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру со списком инструментов пользователя."""
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (ур. {instrument.proficiency_level})",
            callback_data=f"select_inst:{instrument.id}"
        ))

    builder.row(InlineKeyboardButton(text="Готово", callback_data="done"))
    return builder.as_markup()


@router.callback_query(F.data.startswith("practice_"), RegistrationStates.level_practice)
async def update_level_practice(callback: types.CallbackQuery, state: FSMContext):
    level = int(callback.data.split("_")[1])
    id_inst = int(callback.data.split("_")[2])
    try:
        await update_instrument_level(id_inst, level)
    except Exception as e:
        logger.error("Что то пошло не так при обновлении уровня владения в БД")
        return

    data = await state.get_data()
    user_id = data.get("user_id")
    try:
        user = await get_user(user_id)
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя: {e}")
        return

    user_inst = user.instruments
    msg_text = "Ваши инструменты:"

    for inst in user_inst:
        msg_text += f"\n{inst.name}:" + "⭐️" *  inst.proficiency_level

    await callback.message.edit_text(
        text=msg_text,
        reply_markup= get_instrument_rating(user_inst)
    )

@router.callback_query(F.data.startswith("select_inst:"), RegistrationStates.level_practice)
async def view_keyboard_for_rating(callback: types.CallbackQuery, state: FSMContext):
    inst_id = int(callback.data.split(":")[1])


    await state.update_data(inst_id=inst_id)
    await callback.message.edit_text(
        text="Выберите ваш уровень владения:",
        reply_markup=keyboard_rating_practice(inst_id).as_markup()
    )


@router.callback_query(F.data.startswith("done"), RegistrationStates.level_practice)
async def done(callback: types.CallbackQuery, state: FSMContext):
    msg_text = "Отлично! Теперь выберите жанры в которых вы играете:"
    markup = make_keyboard_for_genre([])
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.genre)
    await state.update_data(user_choice_genre= [])
    await state.update_data(own_user_genre=[])


def make_keyboard_for_genre(selected):
    """Клавиатура для жанров"""
    genres = ["Рок", "Поп рок", "Гранж", "Метал", "Ню метал", "Панк", "Свой вариант"]

    buttons = []
    for genre in genres:
        text = f"✅ {genre}" if genre in selected else genre
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"genre_{genre}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("genre_"), RegistrationStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров"""
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
async def own_genre(message: types.Message, state: FSMContext):
    """Обработка кнопки свой вариант для жанров"""
    inst = message.text
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])
    own_user_genre.append(inst)
    msg_text = (f"Свой вариант:{own_user_genre}\n"
                "Отлично! Теперь выберите жанры в которых вы играете:")
    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice))
    await state.set_state(RegistrationStates.genre)

@router.callback_query(F.data.startswith("done"), RegistrationStates.genre)
async def done(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки готово для жанров"""
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])
    all_genres_user = user_choice + own_user_genre
    user_id = data.get("user_id")

    try:
        await update_user_genres(user_id, all_genres_user)
    except Exception as e:
        logger.error(f"Ошибка при добавлении жанров: {e}")
        return


    msg_text = "Отлично! Теперь вам доступен ваш профиль. Для того что ваше объявление привлекло больше внимания, мы советуем вам дополнить информацию в нем."
    button = [
        [types.InlineKeyboardButton(text="Моя анкета", callback_data="my_profile")],
        [types.InlineKeyboardButton(text="Смотреть анкеты", callback_data="search")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=button)
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await state.clear()