from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from handlers.registration.registration_keyboards import (
    make_keyboard_for_instruments,
    make_keyboard_for_genre,
    keyboard_rating_practice,
    get_instrument_rating
)
from database.queries import *
from states.states_registration import RegistrationStates
import logging

logger = logging.getLogger(__name__)

router = Router()

# начало регистрации
@router.callback_query(F.data == "start_registration", RegistrationStates.start_registration)
async def start_search(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Пользователь %s начал регистрацию", callback.from_user.id)

    await state.set_state(RegistrationStates.name)
    await callback.message.answer("Начнем с базовых вопросов."
                         "\nПосле вы можете расширить информацию в профиле "
                         "\nВведите ваше имя: ")
    await callback.answer()

# получаем имя от пользователя
@router.message(F.text, RegistrationStates.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id

    if name.startswith('/'):
        await message.answer("Нельзя чтобы имя начиналось с /"
                                "\nВведите ваше имя")
        return

    if name == "":
        await message.answer("Введите ваше имя")
        return

    try:
        await create_user(user_id=user_id)
        await update_user_name(user_id, name)
    except Exception as e:
        logger.exception("Ошибка при записи имени пользователя %s", user_id)
        return

    await state.update_data(user_id=user_id)
    await state.update_data(name=name)

    logger.info("Пользователь %s указал имя: %s", user_id, name)

    await message.answer("Введите ваш город:")
    await state.set_state(RegistrationStates.city)

# получаем город от пользователя
@router.message(F.text, RegistrationStates.city)
async def get_city(message: types.Message, state: FSMContext):
    city = message.text.lower()
    await state.update_data(city=city)

    data = await state.get_data()
    user_id = data.get("user_id")

    if city.startswith('/'):
        await message.answer("Нельзя чтобы город начинался с /"
                             "\nВведите ваш city")
        return

    if city == "":
        await message.answer("Введите ваш город")
        return

    try:
       await update_user_city(user_id, city)
    except Exception as e:
        logger.exception("Ошибка при записи города пользователя %s", user_id)
        return

    logger.info("Пользователь %s указал город: %s", user_id, city)

    msg_text = "Выберите инструмент/инструменты, которыми вы владеете:"
    markup = make_keyboard_for_instruments([])

    await message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.instrument)
    await state.update_data(user_choice_inst=[])
    await state.update_data(own_user_inst=[])

# если пользователь вдруг заново нажмет /start при регистрации
@router.message(F.text.startswith("/"), RegistrationStates.instrument)
async def block_commands_during_registration(message: types.Message):
    logger.warning("Пользователь %s пытался использовать команду во время регистрации", message.from_user.id)

    await message.answer("Закончите регистрацию, чтобы выйти в главное меню")
    return

# обработка клавиатуры для инструментов
@router.callback_query(F.data.startswith("inst_"), RegistrationStates.instrument)
async def choose_instrument(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_inst", [])

    if choose == "Свой вариант":
        await callback.message.edit_text(text="Напишите инструмент:")
        await state.set_state(RegistrationStates.own_instrument)
        logger.info("Пользователь %s перешёл к вводу собственного инструмента", callback.from_user.id)
        return
    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_instruments(user_choice)
    )
    await state.update_data(user_choice_inst=user_choice)
    logger.info("Пользователь %s обновил выбор инструментов: %s", callback.from_user.id, user_choice)
    await callback.answer()

# обработка кнопки "свой вариант для инструментов"
@router.message(F.text, RegistrationStates.own_instrument)
async def own_instrument(message: types.Message, state: FSMContext):
    inst = message.text

    if inst.startswith('/'):
        await message.answer("Нельзя чтобы название инструмента начиналось с /"
                             "\nНапишите инструмент:")
        return

    data = await state.get_data()
    user_inst = data.get("own_user_inst", [])
    user_choice = data.get("user_choice_inst", [])
    user_inst.append(inst)
    msg_text = (f"Свой вариант:{user_inst}\n"
                "Выберите инструмент/инструменты, которыми вы владеете:")

    logger.info("Пользователь %s ввёл собственный инструмент: %s", message.from_user.id, inst)

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_instruments(user_choice))
    await state.set_state(RegistrationStates.instrument)

# обработка кнопки готово для инструментов
@router.callback_query(F.data.startswith("done"), RegistrationStates.instrument)
async def done_instruments(callback: types.CallbackQuery, state: FSMContext):
    msg_text = "Выберите инструмент который вы хотите оценить:"
    data = await state.get_data()
    logger.debug("FSM data при завершении выбора инструментов: %s", data)

    user_choice_inst = data.get("user_choice_inst", [])
    own_user_inst = data.get("own_user_inst", [])
    user_id = data.get("user_id")

    if len(user_choice_inst) == 0 and len(own_user_inst) == 0:
        await callback.answer("Чтобы идти дальше обязательно выбрать хотя бы один инструмент")
        return

    all_user_inst = user_choice_inst + own_user_inst
    instruments_list = [Instrument(name=inst, proficiency_level=0) for inst in all_user_inst]

    logger.info("Пользователь %s выбрал инструменты: %s", user_id, all_user_inst)

    try:
        await update_user_instruments_for_registration(user_id=user_id, instruments=instruments_list)
        logger.info("Инструменты пользователя %s успешно сохранены в БД", user_id)
    except Exception as e:
        logger.exception("Ошибка при сохранении инструментов пользователя %s", user_id)
        return

    try:
        user_from_db = await get_user(user_id)
        markup = get_instrument_rating(user_from_db.instruments)
        await callback.message.answer(text=msg_text, reply_markup=markup)
        logger.info("Клавиатура оценки инструментов отправлена пользователю %s", user_id)
    except Exception:
        logger.exception("Ошибка при отправке клавиатуры оценки пользователю %s", user_id)
        return

    try:
        await state.set_state(RegistrationStates.level_practice)
        await state.update_data(instruments_list=instruments_list)
        logger.info("FSM состояние обновлено на level_practice пользователя%s", user_id)
    except Exception:
        logger.exception("Ошибка при обновлении состояния FSM пользователя%s", user_id)
    await callback.answer()

# обновление уровня практических умений
@router.callback_query(F.data.startswith("practice_"), RegistrationStates.level_practice)
async def update_level_practice(callback: types.CallbackQuery, state: FSMContext):
    level = int(callback.data.split("_")[1])
    id_inst = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    try:
        await update_instrument_level(id_inst, level)
        logger.info("Пользователь %s обновил уровень инструмента ID=%s до %s", user_id, id_inst, level)
    except Exception:
        logger.exception(
            "Ошибка обновления уровня: пользователь=%s, инструмент_id=%s, уровень=%s",
            user_id, id_inst, level
        )
        return

    try:
        user = await get_user(user_id)
    except Exception:
        logger.exception("Ошибка загрузки профиля пользователя %s после обновления уровня", user_id)
        return

    user_inst = user.instruments
    msg_text = "Ваши инструменты:"

    for inst in user_inst:
        msg_text += f"\n{inst.name}:" + "⭐️" *  inst.proficiency_level

    await callback.message.edit_text(
        text=msg_text,
        reply_markup= get_instrument_rating(user_inst)
    )

# выбор уровня владения инструментом
@router.callback_query(F.data.startswith("select_inst:"), RegistrationStates.level_practice)
async def view_keyboard_for_rating(callback: types.CallbackQuery, state: FSMContext):
    try:
        raw_id = callback.data.split(":", 1)[1]
        logger.info("Получен raw inst_id: %r", raw_id)
        inst_id = int(raw_id)
        logger.info("Пользователь %s открыл оценку инструмента с ID=%s", callback.from_user.id, inst_id)
        await state.update_data(inst_id=inst_id)
        await callback.message.edit_text(
            text="Выберите ваш уровень владения:",
            reply_markup=keyboard_rating_practice(inst_id).as_markup()
        )
    except ValueError as e:
        logger.error("Неверный inst_id: %s", e)
        await callback.answer("Ошибка: неверный ID инструмента.")
    except Exception as e:
        logger.exception("Неизвестная ошибка в view_keyboard_for_rating")
        await callback.answer("Произошла ошибка. Попробуйте позже.")

# переход к выбору жанров
@router.callback_query(F.data == "done_rating", RegistrationStates.level_practice)
async def done_level_practice(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Пользователь %s завершил выбор уровней инструментов", callback.from_user.id)

    msg_text = "Отлично! Теперь выберите жанры в которых вы играете:"
    markup = make_keyboard_for_genre([])
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await state.set_state(RegistrationStates.genre)
    await state.update_data(user_choice_genre= [])
    await state.update_data(own_user_genre=[])
    await callback.answer()

# обработка клавиатуры для жанров
@router.callback_query(F.data.startswith("genre_"), RegistrationStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]

    logger.info("Пользователь %s выбрал/отменил жанр: %s", callback.from_user.id, choose)

    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        logger.info("Пользователь %s запросил ввод собственного жанра", callback.from_user.id)

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

# обработка кнопки свой вариант для жанров
@router.message(F.text, RegistrationStates.own_genre)
async def own_genre(message: types.Message, state: FSMContext):
    genre_text = message.text.strip()
    user_id = message.from_user.id

    if genre_text.startswith("/"):
        await message.answer("Название жанра не может начинаться с /.\nНапишите жанр:")
        return

    logger.info("Пользователь %s ввёл собственный жанр: %s", user_id, genre_text)

    inst = message.text
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])
    own_user_genre.append(inst)

    msg_text = (f"Свой вариант:{own_user_genre}\n"
                "Отлично! Теперь выберите жанры в которых вы играете:")
    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice))
    await state.set_state(RegistrationStates.genre)

# обработка кнопки "готово" для жанров
@router.callback_query(F.data.startswith("done"), RegistrationStates.genre)
async def done_genre(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_choice_genre = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])
    all_genres_user = user_choice_genre + own_user_genre
    user_id = data.get("user_id")

    if len(user_choice_genre) == 0 and len(own_user_genre) == 0:
        await callback.answer("Чтобы идти дальше обязательно выбрать хотя бы один жанр ")
        logger.warning("Пользователь %s попытался завершить регистрацию без жанров", user_id)
        return

    logger.info("Пользователь %s выбрал жанры: %s", user_id, all_genres_user)

    try:
        await update_user_genres(user_id, all_genres_user)
        logger.info("Жанры пользователя %s успешно сохранены в БД", user_id)
    except Exception:
        logger.exception("Ошибка при сохранении жанров пользователя %s", user_id)
        return

    msg_text = "Отлично! Теперь вам доступен ваш профиль. Для того что ваше объявление привлекло больше внимания, мы советуем вам дополнить информацию в нем."
    button = [
        [types.InlineKeyboardButton(text="Моя анкета", callback_data="my_profile")],
        [types.InlineKeyboardButton(text="Смотреть анкеты", callback_data="search")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=button)
    await callback.message.answer(text=msg_text, reply_markup=markup)
    await callback.answer()
    await state.clear()