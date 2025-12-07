import html
import logging

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from handlers.registration.registration_keyboards import (
    make_keyboard_for_instruments,
    make_keyboard_for_genre,
    keyboard_rating_practice,
    get_instrument_rating,
    make_keyboard_for_city, done_keyboard_for_city
)
from database.queries import *
from handlers.start import start
from states.states_registration import RegistrationStates

# Инициализируем логгер
logger = logging.getLogger(__name__)

router = Router()


# начало регистрации
@router.callback_query(F.data == "start_registration")
async def start_search(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал регистрацию", user_id)

    await state.set_state(RegistrationStates.name)

    # Редактируем сообщение, удаляя старую клавиатуру
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # Отправляем новое сообщение с удалением реплай-клавиатуры
    await callback.message.answer(
        text=(
            "👋 <b>Начнем с базовых вопросов!</b>\n\n"
            "Позже вы сможете дополнить свой профиль.\n\n"
            "👤 <b>Введите ваше имя:</b>"
        ),
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )

    await callback.answer()


# получаем имя от пользователя
@router.message(F.text, RegistrationStates.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id

    if name.startswith('/'):
        await message.answer("⚠️ Имя не может начинаться с символа <code>/</code>.\n<b>Введите ваше имя:</b>",
                             parse_mode="HTML")
        return

    if name == "":
        await message.answer("⚠️ <b>Пожалуйста, введите ваше имя.</b>", parse_mode="HTML")
        return

    try:
        await create_user(user_id=user_id)
        await update_user_name(user_id, name)
    except Exception as e:
        logger.exception("Ошибка при записи имени пользователя %s", user_id)
        await message.answer("⚠️ Произошла ошибка при сохранении. Попробуйте снова.")
        return

    await state.update_data(user_id=user_id)
    await state.update_data(name=name)

    logger.info("Пользователь %s указал имя: %s", user_id, name)

    await message.answer(
        text=f"Приятно познакомиться, <b>{html.escape(name)}</b>! 👋\n\n🏙 <b>Выберите ваш город:</b>",
        reply_markup=make_keyboard_for_city(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.city)


# получаем город от пользователя
@router.callback_query(F.data.startswith("city_"), RegistrationStates.city)
async def get_city(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[1]
    await state.update_data(city=city)

    data = await state.get_data()
    user_id = data.get("user_id")  # Получаем user_id из FSM

    if city.startswith('Свой вариант'):
        await callback.message.edit_text(text="🏙 <b>Напишите название вашего города:</b>", parse_mode="HTML")
        await state.set_state(RegistrationStates.own_city)
        logger.info("Пользователь %s перешёл к вводу собственного города", callback.from_user.id)
        return

    try:
        await update_user_city(user_id, city)
    except Exception as e:
        logger.exception("Ошибка при записи города пользователя %s", user_id)
        return

    logger.info("Пользователь %s указал город: %s", user_id, city)

    msg_text = f"✅ Ваш город: <b>{html.escape(city)}</b>"
    markup = done_keyboard_for_city()

    await callback.message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
    await state.set_state(RegistrationStates.msg_about_city)
    await callback.answer()


# обработка кнопки "свой вариант для городов"
@router.message(F.text, RegistrationStates.own_city)
async def own_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    user_id = message.from_user.id  # Используем user_id из сообщения

    if city.startswith('/'):
        await message.answer("⚠️ Название города не может начинаться с <code>/</code>.\n<b>Напишите город:</b>",
                             parse_mode="HTML")
        return

    data = await state.get_data()
    # user_id = data.get("user_id") # уже определен из message.from_user.id

    try:
        await update_user_city(user_id, city)
    except Exception as e:
        logger.exception("Ошибка при записи города пользователя %s", user_id)
        return

    logger.info("Пользователь %s ввёл собственный город: %s", user_id, city)

    msg_text = f"✅ Ваш город: <b>{html.escape(city)}</b>"
    markup = done_keyboard_for_city()
    await message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
    await state.set_state(RegistrationStates.msg_about_city)


# подтверждение, что город введен правильно
@router.callback_query(F.data, RegistrationStates.msg_about_city)
async def done_for_city(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id  # Получаем user_id

    if callback.data == "right":
        logger.info("Пользователь %s подтвердил, что ввел город корректно", user_id)
        msg_text = "🎸 <b>Инструменты</b>\n\nВыберите инструмент/инструменты, которыми вы владеете:"
        markup = make_keyboard_for_instruments([])

        await callback.message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
        await state.set_state(RegistrationStates.instrument)
        await state.update_data(user_choice_inst=[])
        await state.update_data(own_user_inst=[])

    if callback.data == "wrong":
        logger.info("Пользователь %s хочет изменить город", user_id)
        await callback.message.answer(text="🏙 <b>Выберите город:</b>", reply_markup=make_keyboard_for_city(),
                                      parse_mode="HTML")
        await state.set_state(RegistrationStates.city)

    await callback.answer()


# если пользователь вдруг заново нажмет /start при регистрации
@router.message(F.text.startswith("/"), RegistrationStates.genre)
@router.message(F.text.startswith("/"), RegistrationStates.level_practice)
@router.message(F.text.startswith("/"), RegistrationStates.msg_about_city)
@router.message(F.text.startswith("/"), RegistrationStates.city)
@router.message(F.text.startswith("/"), RegistrationStates.instrument)
async def block_commands_during_registration(message: types.Message):
    logger.warning("Пользователь %s пытался использовать команду во время регистрации", message.from_user.id)
    await message.answer("⚠️ <b>Пожалуйста, закончите регистрацию, чтобы выйти в главное меню.</b>", parse_mode="HTML")
    return


# обработка клавиатуры для инструментов
@router.callback_query(F.data.startswith("inst_"), RegistrationStates.instrument)
async def choose_instrument(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_inst", [])
    user_id = callback.from_user.id

    if choose == "Свой вариант":
        await callback.message.edit_text(text="📝 <b>Напишите название инструмента:</b>", parse_mode="HTML")
        await state.set_state(RegistrationStates.own_instrument)
        logger.info("Пользователь %s перешёл к вводу собственного инструмента", user_id)
        return

    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_instruments(user_choice)
    )
    await state.update_data(user_choice_inst=user_choice)
    logger.info("Пользователь %s обновил выбор инструментов: %s", user_id, user_choice)
    await callback.answer()


# обработка кнопки "свой вариант для инструментов"
@router.message(F.text, RegistrationStates.own_instrument)
async def own_instrument(message: types.Message, state: FSMContext):
    inst = message.text.strip()
    user_id = message.from_user.id

    if inst.startswith('/'):
        await message.answer(
            "⚠️ Название инструмента не может начинаться с <code>/</code>.\n<b>Напишите инструмент:</b>",
            parse_mode="HTML")
        return

    data = await state.get_data()
    user_inst = data.get("own_user_inst", [])
    user_choice = data.get("user_choice_inst", [])
    user_inst.append(inst)

    # Красивое перечисление добавленных
    formatted_own = ", ".join([f"<i>{html.escape(i)}</i>" for i in user_inst])

    msg_text = (f"✅ Свой вариант добавлен: {formatted_own}\n\n"
                "<b>Выберите инструмент/инструменты, которыми вы владеете:</b>")

    logger.info("Пользователь %s ввёл собственный инструмент: %s", user_id, inst)

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_instruments(user_choice), parse_mode="HTML")
    await state.set_state(RegistrationStates.instrument)


# обработка кнопки готово для инструментов
@router.callback_query(F.data.startswith("done"), RegistrationStates.instrument)
async def done_instruments(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.debug("Пользователь %s. FSM data при завершении выбора инструментов: %s", user_id, data)

    user_choice_inst = data.get("user_choice_inst", [])
    own_user_inst = data.get("own_user_inst", [])

    if len(user_choice_inst) == 0 and len(own_user_inst) == 0:
        await callback.answer("⚠️ Выберите хотя бы один инструмент!", show_alert=True)
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
        msg_text = "🎹 <b>Уровень владения</b>\n\nВыберите инструмент, который хотите оценить:"

        await callback.message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
        logger.info("Клавиатура оценки инструментов отправлена пользователю %s", user_id)
    except Exception:
        logger.exception("Ошибка при отправке клавиатуры оценки пользователю %s", user_id)
        return

    try:
        await state.set_state(RegistrationStates.level_practice)
        await state.update_data(instruments_list=instruments_list)
        logger.info("FSM состояние обновлено на level_practice для пользователя %s", user_id)  # Исправлен формат
    except Exception:
        logger.exception("Ошибка при обновлении состояния FSM пользователя %s", user_id)  # Исправлен формат

    await callback.answer()


# обновление уровня практических умений
@router.callback_query(F.data.startswith("practice_"), RegistrationStates.level_practice)
async def update_level_practice(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    try:
        level = int(callback.data.split("_")[1])
        id_inst = int(callback.data.split("_")[2])

        await update_instrument_level(id_inst, level)
        logger.info("Пользователь %s обновил уровень инструмента ID=%s до %s", user_id, id_inst, level)
    except Exception:
        logger.exception("Ошибка обновления уровня для пользователя %s", user_id)  # Добавлен user_id
        return

    try:
        user = await get_user(user_id)
    except Exception:
        logger.exception("Ошибка загрузки профиля для пользователя %s", user_id)  # Добавлен user_id
        return

    user_inst = user.instruments

    # Формируем красивый список с оценками
    msg_lines = ["🎹 <b>Ваши инструменты:</b>\n"]
    for inst in user_inst:
        stars = "⭐️" * inst.proficiency_level if inst.proficiency_level else "—"
        msg_lines.append(f"• <b>{html.escape(inst.name)}</b>: {stars}")

    msg_text = "\n".join(msg_lines)

    await callback.message.edit_text(
        text=msg_text,
        reply_markup=get_instrument_rating(user_inst),
        parse_mode="HTML"
    )


# выбор уровня владения инструментом
@router.callback_query(F.data.startswith("select_inst:"), RegistrationStates.level_practice)
async def view_keyboard_for_rating(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    try:
        raw_id = callback.data.split(":", 1)[1]
        logger.info("Пользователь %s. Получен raw inst_id: %r", user_id, raw_id)  # Добавлен user_id
        inst_id = int(raw_id)
        logger.info("Пользователь %s открыл оценку инструмента с ID=%s", user_id, inst_id)
        await state.update_data(inst_id=inst_id)

        await callback.message.edit_text(
            text="📊 <b>Выберите ваш уровень владения:</b>",
            reply_markup=keyboard_rating_practice(inst_id).as_markup(),
            parse_mode="HTML"
        )
    except ValueError as e:
        logger.error("Пользователь %s. Неверный inst_id: %s", user_id, e)  # Добавлен user_id
        await callback.answer("Ошибка: неверный ID инструмента.")
    except Exception as e:
        logger.exception("Пользователь %s. Неизвестная ошибка в view_keyboard_for_rating", user_id)  # Добавлен user_id
        await callback.answer("Произошла ошибка. Попробуйте позже.")


# переход к выбору жанров
@router.callback_query(F.data == "done_rating", RegistrationStates.level_practice)
async def done_level_practice(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Пользователь %s завершил выбор уровней инструментов", callback.from_user.id)

    msg_text = "🎶 <b>Жанры</b>\n\nОтлично! Теперь выберите жанры, в которых вы играете:"
    markup = make_keyboard_for_genre([])

    await callback.message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
    await state.set_state(RegistrationStates.genre)
    await state.update_data(user_choice_genre=[])
    await state.update_data(own_user_genre=[])
    await callback.answer()


# обработка клавиатуры для жанров
@router.callback_query(F.data.startswith("genre_"), RegistrationStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    user_id = callback.from_user.id

    logger.info("Пользователь %s выбрал/отменил жанр: %s", user_id, choose)

    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        logger.info("Пользователь %s запросил ввод собственного жанра", user_id)
        await callback.message.edit_text(text="📝 <b>Напишите название жанра:</b>", parse_mode="HTML")
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
        await message.answer("⚠️ Название жанра не может начинаться с <code>/</code>.\n<b>Напишите жанр:</b>",
                             parse_mode="HTML")
        return

    logger.info("Пользователь %s ввёл собственный жанр: %s", user_id, genre_text)

    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])
    own_user_genre.append(genre_text)

    formatted_own = ", ".join([f"<i>{html.escape(g)}</i>" for g in own_user_genre])

    msg_text = (f"✅ Свой вариант добавлен: {formatted_own}\n\n"
                "<b>Выберите еще жанры или нажмите 'Готово':</b>")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice), parse_mode="HTML")
    await state.set_state(RegistrationStates.genre)


# обработка кнопки "готово" для жанров
@router.callback_query(F.data.startswith("done"), RegistrationStates.genre)
async def done_genre(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    user_choice_genre = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])
    all_genres_user = user_choice_genre + own_user_genre

    if len(user_choice_genre) == 0 and len(own_user_genre) == 0:
        await callback.answer("⚠️ Выберите хотя бы один жанр!", show_alert=True)
        logger.warning("Пользователь %s попытался завершить регистрацию без жанров", user_id)
        return

    logger.info("Пользователь %s выбрал жанры: %s", user_id, all_genres_user)

    try:
        await update_user_genres(user_id, all_genres_user)
        logger.info("Жанры пользователя %s успешно сохранены в БД", user_id)
    except Exception:
        logger.exception("Ошибка при сохранении жанров пользователя %s", user_id)
        return

    msg_text = (
        "🎉 <b>Отлично! Регистрация завершена.</b>\n\n"
        "Теперь вам доступен ваш профиль.\n"
        "💡 <i>Чтобы ваше объявление привлекло больше внимания, рекомендуем дополнить информацию в профиле.</i>"
    )

    button = [
        [types.InlineKeyboardButton(text="👤 Моя анкета", callback_data="my_profile")],
        [types.InlineKeyboardButton(text="🎸 Зарегистрировать группу", callback_data="start_band_registration")],
        [types.InlineKeyboardButton(text="🔍 Смотреть анкеты", callback_data="show_with_registration")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=button)

    await callback.message.answer(text=msg_text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()
    await state.clear()