import logging
from contextlib import suppress

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

# Импортируем все необходимые функции БД и клавиатуры, как в оригинале
from database.queries import get_random_profile, get_random_group, save_user_interaction, save_group_interaction, \
    get_profile_which_not_action, get_band_which_not_action
from handlers.show_profiles.show_keyboards import choose_keyboard_for_show, \
    show_reply_keyboard_for_unregistered_users, show_reply_keyboard_for_registered_users, \
    make_instrument_filter_keyboard, make_city_filter_keyboard, make_genre_filter_keyboard, make_age_filter_keyboard, \
    make_experience_filter_keyboard, make_level_filter_keyboard, get_group_filter_menu_keyboard, \
    make_seriousness_filter_keyboard
from handlers.show_profiles.show_keyboards import get_filter_menu_keyboard
from handlers.start import start
from states.states_show_profiles import ShowProfiles
from database.enums import Actions

from aiogram.fsm.state import default_state

logger = logging.getLogger(__name__)

router = Router()


# Вспомогательная функция для отображения рейтинга звездочками
def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level


# --- ХЕНДЛЕРЫ ПРОСМОТРА ---

# старт просмотр анкет, если пользователь не зарегистрирован
@router.callback_query(F.data == "show_without_registration")
async def start_show_unregistered_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s начал просмотр анкет без регистрации", user_id)

    msg = "<b>Выберите, что вы хотите смотреть:</b> 👇"

    await callback.message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.update_data(registered=False)
    await state.set_state(ShowProfiles.choose)
    await callback.answer()


# старт просмотр анкет, если пользователь зарегистрирован (Callback)
@router.callback_query(F.data == "show_with_registration")
async def start_show_registered_user_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s начал просмотр анкет c регистрацией", user_id)

    msg = "<b>Выберите, что вы хотите смотреть:</b> 👇"

    await callback.message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.update_data(registered=True)
    await state.set_state(ShowProfiles.choose)
    await callback.answer()


# старт просмотр анкет, если пользователь зарегистрирован (Message)
@router.message(F.text.startswith("🔍 Смотреть анкеты"))
async def start_show_registered_user_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("Пользователь ID=%s начал просмотр анкет c регистрацией", user_id)

    msg = "<b>Выберите, что вы хотите смотреть:</b> 👇"

    await message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.update_data(registered=True)
    await state.set_state(ShowProfiles.choose)


# выбор, что хочет смотреть пользователь
@router.callback_query(F.data.startswith("chs_"), ShowProfiles.choose)
async def choose_user(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await state.update_data(user_id=user_id, current_target_id=None, current_target_type=None)

    if choose == "bands":
        logger.info("Пользователь ID=%s выбрал просмотр групп", user_id)
        await state.set_state(ShowProfiles.show_bands)
        await show_bands(callback.message, state)

    if choose == "artist":
        logger.info("Пользователь ID=%s выбрал просмотр соло артистов", user_id)
        await state.set_state(ShowProfiles.show_profiles)
        await show_profiles(callback.message, state)

    await callback.answer()


# показывает анкеты групп
@router.message(F.text.startswith("Следующая анкета"), ShowProfiles.show_bands)
async def show_bands(message: types.Message, state: FSMContext):
    data = await state.get_data()
    registered = data.get("registered")
    markup: types.ReplyKeyboardMarkup

    user_id = data.get("user_id")
    # Логируем начало процесса
    logger.info("Пользователь ID=%s нажал кнопку 'Следующая анкета' (группы)", user_id)

    # --- ЛОГИКА SKIP (Пропуск предыдущей анкеты) ---
    prev_target_id = data.get("current_target_id")
    prev_target_type = data.get("current_target_type")

    if prev_target_id and prev_target_type == "group" and registered:
        try:
            await save_group_interaction(user_id, prev_target_id, Actions.SKIP)
            logger.info("Записан автоматический SKIP: user ID=%s -> group ID=%s", user_id, prev_target_id)
        except Exception as e:
            logger.error("Ошибка у пользователя ID=%s при записи SKIP: %s", user_id, e)

    # --- ПОЛУЧЕНИЕ АНКЕТЫ ---
    profile_msg = ""

    # Достаем фильтры именно для групп
    group_filters = data.get("group_filters", {})

    try:
        logger.info("Пользователь ID=%s ищет группу. Фильтры: %s", user_id, group_filters)

        if not registered:
            # Гости смотрят случайные группы без фильтров
            band = await get_random_group()
        else:
            # Зарегистрированные смотрят с учетом фильтров и исключений
            band = await get_band_which_not_action(user_id, filters=group_filters)

        # Если группа не найдена
        if not band:
            if registered and group_filters:
                # Если были включены фильтры
                await message.answer(
                    "🎸 <b>По вашим фильтрам группы не найдены 😔</b>\n"
                    "Попробуйте изменить параметры (Город, Жанры, Уровень)."
                )
                logger.info("Пользователю ID=%s не найдены группы по фильтрам: %s", user_id, group_filters)
            else:
                # Если фильтров нет или это гость
                await message.answer("🏁 <b>Анкеты групп закончились!</b> Попробуйте позже.")
                logger.info("Для пользователя ID=%s анкеты групп закончились", user_id)

            # Сбрасываем текущую цель, чтобы не лайкнуть "пустоту"
            await state.update_data(current_target_id=None, current_target_type=None)
            return

    except Exception as e:
        logger.exception("Не получилось получить данные у пользователя ID=%s о группе", user_id)
        await message.answer("Произошла ошибка при загрузке анкеты.")
        return

    # Запоминаем текущую группу
    await state.update_data(current_target_id=band.id, current_target_type="group")

    # --- ФОРМИРОВАНИЕ ТЕКСТА АНКЕТЫ ---
    name = band.name if band.name is not None else "Не указано"
    year = band.formation_date if band.formation_date is not None else "Не указано"
    city = band.city if band.city is not None else "Не указано"

    # Получение списка жанров
    genres_list = band.genres if band.genres is not None else []
    genre_names = [genre_entity.name for genre_entity in genres_list]
    genres_display = ", ".join(genre_names) if genre_names else "Не указано"

    # Вариант для ГОСТЯ
    if not registered:
        markup = show_reply_keyboard_for_unregistered_users()
        profile_msg = (
            f"🎸 <b>Название:</b> {name} \n"
            f"🏙 <b>Город:</b> {city} \n"
            f"📅 <b>Год основания:</b> {year}\n"
            f"🎼 <b>Жанры:</b> {genres_display}\n\n"
            "🔒 <i>Хотите видеть больше информации о группах?</i>\n"
            "<b>Тогда пройдите регистрацию!</b>\n"
            "Больше информации по кнопке «Подробнее»."
        )

    # Вариант для ЗАРЕГИСТРИРОВАННОГО
    if registered:
        markup = show_reply_keyboard_for_registered_users()
        description = band.description if band.description is not None else "Не указано"

        # Отображение уровня (если это Enum, берем .value, если строка - оставляем)
        level_raw = band.seriousness_level
        if hasattr(level_raw, 'value'):
            level = level_raw.value
        else:
            level = level_raw if level_raw else "Не указано"

        profile_msg = (
            f"🎸 <b>Название:</b> {name}\n"
            f"📅 <b>Год основания:</b> {year}\n"
            f"🏙 <b>Город:</b> {city}\n"
            f"📊 <b>Уровень:</b> {level}\n"
            f"🎼 <b>Жанры:</b> <i>{genres_display}</i>\n"
            f"\n"
            f"📝 <b>О себе:</b>\n"
            f"<i>{description}</i>\n"
            f"\n"
            "👇 <b>Выберите действие:</b>"
        )

    await message.answer(text=profile_msg, reply_markup=markup)

# показывает анкеты пользователей
@router.message(F.text.startswith("Следующая анкета"), ShowProfiles.show_profiles)
async def show_profiles(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    logger.info("Пользователь ID=%s нажал кнопку Следующая анкета (соло)", user_id)
    registered = data.get("registered")

    filters = data.get("filters")

    markup: types.ReplyKeyboardMarkup

    prev_target_id = data.get("current_target_id")
    prev_target_type = data.get("current_target_type")

    # Логика записи пропуска
    if prev_target_id and prev_target_type == "user" and registered:
        try:
            await save_user_interaction(user_id, prev_target_id, Actions.SKIP)
            logger.info("Записан автоматический SKIP: swiper ID=%s -> target ID=%s", user_id, prev_target_id)
        except Exception as e:
            logger.error("Ошибка у пользователя ID=%s при записи SKIP: %s", user_id, e)

    profile_msg = ""

    try:
        if not registered:
            logger.info("Гость ID=%s: ищем рандомный профиль БЕЗ фильтров", user_id)
            user = await get_random_profile(swiper_id=user_id, filters=None)
        else:
            logger.info("Регистрация есть: ищем профиль С фильтрами: %s у пользователя ID=%s", filters, user_id)
            user = await get_random_profile(swiper_id=user_id, filters=filters)

        if not user:
            if registered and filters:
                await message.answer(
                    "🕵️‍♂️ <b>По вашим фильтрам анкеты не найдены 😔</b>\n"
                    "Попробуйте изменить параметры (Город, Жанры и т.д.)."
                )
                logger.info("Пользователю ID=%s не найдены анкеты по фильтрам: %s", user_id, filters)
            else:
                await message.answer("🏁 <b>Анкеты пользователей закончились!</b> Попробуйте позже.")
                logger.info("Для пользователя ID=%s анкеты пользователей закончились", user_id)

            await state.update_data(current_target_id=None, current_target_type=None)
            return

    except Exception as e:
        logger.exception("Ошибка у пользователя ID=%s при получении анкеты", user_id)
        return

    await state.update_data(current_target_id=user.id, current_target_type="user")

    genres_list = user.genres or []
    genre_names = [genre_entity.name for genre_entity in genres_list]
    genres_display = ", ".join(genre_names) if genre_names else "Не указано"

    instruments_lines = []
    if user.instruments:
        for instrument in user.instruments:
            proficiency_level = instrument.proficiency_level if instrument.proficiency_level is not None else 0
            stars_proficiency = rating_to_stars(proficiency_level)
            instruments_lines.append(
                f"  • <b>{instrument.name}</b>: {stars_proficiency}"
            )
        instruments_display = "\n".join(instruments_lines)
    else:
        instruments_display = "Не указаны"

    if not registered:
        profile_msg = (
            f"👤 <b>Имя:</b> {user.name or 'Не указано'}\n"
            f"🏙 <b>Город:</b> {user.city or 'Не указано'}\n"
            f"🎼 <b>Жанры:</b> {genres_display}\n"
            f"🎹 <b>Инструменты:</b> \n{instruments_display}\n"
            "🔒 <i>Хотите видеть больше информации об артистах?</i>\n"
            "<b>Тогда пройдите регистрацию!</b>\n"
            "Больше информации по кнопке «Подробнее»."
        )
        markup = show_reply_keyboard_for_unregistered_users()

    if registered:
        markup = show_reply_keyboard_for_registered_users()

        chat_id = message.chat.id if isinstance(message, types.Message) else message.message.chat.id
        knowledge_level = user.theoretical_knowledge_level if user.theoretical_knowledge_level is not None else 0
        stars_knowledge = rating_to_stars(knowledge_level)
        experience_display = getattr(user.has_performance_experience, 'value', 'Не указано')
        about_me_display = user.about_me if user.about_me else "Не указано"
        external_link_display = user.external_link if user.external_link else "Не указана"

        # Если есть ссылка, делаем её кликабельной, иначе оставляем текст
        if external_link_display and external_link_display != "Не указана":
            link_html = f"<a href='{external_link_display}'>{external_link_display}</a>"
        else:
            link_html = external_link_display

        profile_msg = (
            f"👤 <b>Имя:</b> {user.name or 'Не указано'}\n"
            f"🎂 <b>Возраст:</b> {user.age or 'Не указано'}\n"
            f"🏙 <b>Город:</b> {user.city or 'Не указано'}\n\n"
            f"📝 <b>О себе:</b>\n"
            f"<i>{about_me_display}</i>\n\n"
            f"🧠 <b>Уровень теоретических знаний:</b> {stars_knowledge}\n"
            f"🎤 <b>Опыт выступлений:</b> {experience_display or 'Не указано'}\n\n"
            f"🔗 <b>Внешняя ссылка:</b> {link_html}\n\n"
            f"🎼 <b>Любимые жанры:</b> {genres_display}\n\n"
            f"🎹 <b>Инструменты:</b>\n"
            f"{instruments_display}\n\n"
        )

        if user.photo_path:
            try:
                await message.send_photo(chat_id, photo=user.photo_path, caption="📸 <b>Фото профиля:</b>")
                logger.info("Пользователю ID=%s отправлено фото профиля ID=%s", user_id, user.id)
            except Exception as e:
                logger.error("Ошибка отправки фото для пользователя ID=%s: %s", user_id, e)

        if user.audio_path:
            try:
                await message.send_audio(chat_id, audio=user.audio_path, caption="🎧 <b>Демо-трек:</b>")
                logger.info("Пользователю ID=%s отправлено аудио профиля ID=%s", user_id, user.id)
            except Exception as e:
                logger.error("Ошибка отправки аудио для пользователя ID=%s: %s", user_id, e)

    await message.answer(text=profile_msg, reply_markup=markup)


# возврат в главное меню
@router.message(F.text.startswith("Вернуться на главную"), ShowProfiles.show_bands)
@router.message(F.text.startswith("Вернуться на главную"), ShowProfiles.show_profiles)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("Пользователь ID=%s вернулся в главное меню", user_id)
    await start(message, state)


# обработка кнопки "Подробнее"
@router.message(F.text.startswith("Подробнее"), ShowProfiles.show_bands)
@router.message(F.text.startswith("Подробнее"), ShowProfiles.show_profiles)
async def info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("Пользователь ID=%s нажал кнопку 'Подробнее'", user_id)
    data = await state.get_data()
    registered = data.get("registered")
    if registered:
        return
    msg = (
        "🔒 <b>Понравилась анкета?</b>\n\n"
        "Чтобы ставить лайки, надо пройти регистрацию!\n"
        "Также после регистрации вы сможете видеть:\n"
        "✅ Опыт выступлений\n"
        "✅ Информацию о музыкантах и их контактные данные\n"
        "✅ Аудио файлы музыкантов\n"
        "✅ И многое другое!"
    )

    await message.answer(text=msg, reply_markup=show_reply_keyboard_for_unregistered_users())


# обработка лайка
@router.message(F.text.startswith("❤️ Оценить анкету"), ShowProfiles.show_bands)
@router.message(F.text.startswith("❤️ Оценить анкету"), ShowProfiles.show_profiles)
async def like(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    target_id = data.get("current_target_id")
    target_type = data.get("current_target_type")

    logger.info("Пользователь ID=%s ставит LIKE на %s ID=%s", user_id, target_type, target_id)

    if not user_id or not target_id:
        logger.warning("Пользователь ID=%s попытался поставить лайк, но target_id не найден", message.from_user.id)
        return await message.answer("⚠️ Не удалось определить текущую анкету. Нажмите 'Следующая анкета'.")

    if target_type == "user":
        await save_user_interaction(user_id, target_id, Actions.LIKE)
        await message.answer("💖 <b>Вы оценили данного музыканта</b>")

    elif target_type == "group":
        await save_group_interaction(user_id, target_id, Actions.LIKE)
        await message.answer("🔥 <b>Вы оценили группу!</b> Они увидят ваш интерес.")

    await state.update_data(current_target_id=None, current_target_type=None)


# --- ФИЛЬТРЫ ---

# открытие меню фильтров
@router.message(F.text == "Фильтр 🔍", ShowProfiles.show_profiles)
async def open_filter_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("Пользователь ID=%s открыл меню фильтров", user_id)
    data = await state.get_data()

    # Сохраняем текущее состояние просмотра, чтобы потом вернуться
    current_show_state = await state.get_state()
    await state.update_data(previous_show_state=current_show_state)

    # Получаем текущие фильтры (если они есть)
    current_filters = data.get('filters', {})

    await message.answer(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(current_filters)
    )
    await state.set_state(ShowProfiles.filter_menu)


# возврат из меню фильтров
@router.callback_query(F.data == "back_from_filters", ShowProfiles.filter_menu)
async def back_to_showing(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    # Восстанавливаем предыдущее состояние просмотра
    previous_state = data.get('previous_show_state', ShowProfiles.show_profiles)

    await state.set_state(previous_state)
    await callback.message.delete()

    await callback.message.answer(
        "✅ <b>Настройки фильтров применены.</b>",
        reply_markup=show_reply_keyboard_for_registered_users()
    )
    logger.info("Пользователь ID=%s вернулся к просмотру, фильтры применены", user_id)
    await callback.answer("Фильтры сохранены!")


@router.callback_query(F.data == "reset_all_filters", ShowProfiles.filter_menu)
async def reset_all_filters_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # Очищаем фильтры в машине состояний
    await state.update_data(filters={})

    # Обновляем текст и клавиатуру, чтобы показать, что все сброшено
    await callback.message.edit_text(
        "🧹 <b>Все фильтры сброшены.</b> Вы будете видеть все анкеты.",
        reply_markup=get_filter_menu_keyboard({})  # Передаем пустой словарь
    )
    logger.info("Пользователь ID=%s сбросил все фильтры", user_id)
    await callback.answer("Фильтры полностью сброшены!")


@router.callback_query(F.data == "set_filter_instruments", ShowProfiles.filter_menu)
async def start_set_instruments_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра инструментов", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    selected = filters.get('instruments', [])

    keyboard = make_instrument_filter_keyboard(selected)

    await callback.message.edit_text(
        "🛠️ <b>Инструменты</b>\n"
        "Выберите инструменты, анкеты с которыми хотите видеть:",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_instruments)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_inst_"), ShowProfiles.filter_instruments)
async def toggle_instrument_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    instrument_name = callback.data.split("filter_inst_")[1]
    data = await state.get_data()
    filters = data.get('filters', {})
    selected_instruments = filters.get('instruments', [])

    action = "добавил"
    if instrument_name in selected_instruments:
        selected_instruments.remove(instrument_name)
        action = "удалил"
    else:
        selected_instruments.append(instrument_name)

    logger.info("Пользователь ID=%s %s инструмент '%s' в фильтр", user_id, action, instrument_name)

    filters['instruments'] = selected_instruments
    await state.update_data(filters=filters)

    keyboard = make_instrument_filter_keyboard(selected_instruments)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "filter_inst_custom", ShowProfiles.filter_instruments)
async def prompt_custom_instrument(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s запросил ввод кастомного инструмента для фильтра", user_id)
    await callback.message.edit_text("📝 <b>Введите название инструмента</b>, которое вы хотите добавить в фильтр:")
    await state.set_state(ShowProfiles.filter_instruments_custom)
    await callback.answer()


@router.message(ShowProfiles.filter_instruments_custom)
async def save_custom_instrument_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_instrument = message.text.strip()

    if not new_instrument:
        logger.warning("Пользователь ID=%s ввел пустое название инструмента для фильтра", user_id)
        await message.answer("⚠️ Пожалуйста, введите название инструмента.")
        return

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_instruments = filters.get('instruments', [])

    if new_instrument not in selected_instruments:
        selected_instruments.append(new_instrument)
        filters['instruments'] = selected_instruments
        await state.update_data(filters=filters)
        logger.info("Пользователь ID=%s добавил кастомный инструмент '%s' в фильтр", user_id, new_instrument)
    else:
        logger.info("Пользователь ID=%s повторно ввел существующий инструмент '%s'", user_id, new_instrument)

    keyboard = make_instrument_filter_keyboard(selected_instruments)
    await message.answer(
        f"✅ Инструмент <b>{new_instrument}</b> добавлен в фильтр.\nВыберите еще или нажмите 'Готово'.",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_instruments)


@router.callback_query(F.data == "done_filter_instruments", ShowProfiles.filter_instruments)
async def done_instrument_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    instruments_count = len(filters.get('instruments', []))
    logger.info("Пользователь ID=%s сохранил фильтр инструментов (всего %d)", user_id, instruments_count)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Инструменты сохранены!")


@router.callback_query(F.data == "set_filter_city", ShowProfiles.filter_menu)
async def start_set_city_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра городов", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    selected = filters.get('cities', [])

    keyboard = make_city_filter_keyboard(selected)

    await callback.message.edit_text(
        "🏙️ <b>Города</b>\n"
        "Выберите города, в которых хотите искать анкеты:",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_city)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_city_"), ShowProfiles.filter_city)
async def toggle_city_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == "filter_city_custom_prompt":
        return

    city_name = callback.data.split("filter_city_")[1]

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_cities = filters.get('cities', [])

    action = "добавил"
    if city_name in selected_cities:
        selected_cities.remove(city_name)
        action = "удалил"
    else:
        selected_cities.append(city_name)

    logger.info("Пользователь ID=%s %s город '%s' в фильтр", user_id, action, city_name)

    filters['cities'] = selected_cities
    await state.update_data(filters=filters)

    keyboard = make_city_filter_keyboard(selected_cities)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "filter_city_custom_prompt", ShowProfiles.filter_city)
async def prompt_custom_city(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s запросил ввод кастомного города для фильтра", user_id)
    await callback.message.edit_text("📝 <b>Введите название города</b>, которое вы хотите добавить в фильтр:")
    await state.set_state(ShowProfiles.filter_city_custom)
    await callback.answer()


@router.message(ShowProfiles.filter_city_custom)
async def save_custom_city_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_city = message.text.strip()

    if not new_city:
        logger.warning("Пользователь ID=%s ввел пустое название города для фильтра", user_id)
        await message.answer("⚠️ Пожалуйста, введите название города.")
        return

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_cities = filters.get('cities', [])

    if new_city not in selected_cities:
        selected_cities.append(new_city)
        filters['cities'] = selected_cities
        await state.update_data(filters=filters)
        logger.info("Пользователь ID=%s добавил кастомный город '%s' в фильтр", user_id, new_city)
    else:
        logger.info("Пользователь ID=%s повторно ввел существующий город '%s'", user_id, new_city)

    keyboard = make_city_filter_keyboard(selected_cities)
    await message.answer(
        f"✅ Город <b>{new_city}</b> добавлен в фильтр.\nВыберите еще или нажмите 'Готово'.",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_city)


@router.callback_query(F.data == "done_filter_city", ShowProfiles.filter_city)
async def done_city_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    cities_count = len(filters.get('cities', []))
    logger.info("Пользователь ID=%s сохранил фильтр городов (всего %d)", user_id, cities_count)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Города сохранены!")


@router.callback_query(F.data == "set_filter_genres", ShowProfiles.filter_menu)
async def start_set_genres_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра жанров", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    selected = filters.get('genres', [])

    keyboard = make_genre_filter_keyboard(selected)

    await callback.message.edit_text(
        "🎶 <b>Жанры</b>\n"
        "Выберите жанры, анкеты с которыми хотите видеть:",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_genres)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_genre_"), ShowProfiles.filter_genres)
async def toggle_genre_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == "filter_genre_custom_prompt":
        return

    genre_name = callback.data.split("filter_genre_")[1]

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_genres = filters.get('genres', [])

    action = "добавил"
    if genre_name in selected_genres:
        selected_genres.remove(genre_name)
        action = "удалил"
    else:
        selected_genres.append(genre_name)

    logger.info("Пользователь ID=%s %s жанр '%s' в фильтр", user_id, action, genre_name)

    filters['genres'] = selected_genres
    await state.update_data(filters=filters)

    keyboard = make_genre_filter_keyboard(selected_genres)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "filter_genre_custom_prompt", ShowProfiles.filter_genres)
async def prompt_custom_genre(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s запросил ввод кастомного жанра для фильтра", user_id)
    await callback.message.edit_text("📝 <b>Введите название жанра</b>, которое вы хотите добавить в фильтр:")
    await state.set_state(ShowProfiles.filter_genres_custom)
    await callback.answer()


@router.message(ShowProfiles.filter_genres_custom)
async def save_custom_genre_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_genre = message.text.strip()

    if not new_genre:
        logger.warning("Пользователь ID=%s ввел пустое название жанра для фильтра", user_id)
        await message.answer("⚠️ Пожалуйста, введите название жанра.")
        return

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_genres = filters.get('genres', [])

    if new_genre not in selected_genres:
        selected_genres.append(new_genre)
        filters['genres'] = selected_genres
        await state.update_data(filters=filters)
        logger.info("Пользователь ID=%s добавил кастомный жанр '%s' в фильтр", user_id, new_genre)
    else:
        logger.info("Пользователь ID=%s повторно ввел существующий жанр '%s'", user_id, new_genre)

    keyboard = make_genre_filter_keyboard(selected_genres)
    await message.answer(
        f"✅ Жанр <b>{new_genre}</b> добавлен в фильтр.\nВыберите еще или нажмите 'Готово'.",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_genres)


@router.callback_query(F.data == "done_filter_genres", ShowProfiles.filter_genres)
async def done_genre_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    genres_count = len(filters.get('genres', []))
    logger.info("Пользователь ID=%s сохранил фильтр жанров (всего %d)", user_id, genres_count)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Жанры сохранены!")


@router.callback_query(F.data == "set_filter_age", ShowProfiles.filter_menu)
async def start_set_age_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра возраста", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    current_mode = filters.get('age_mode', 'all')

    await callback.message.edit_text(
        "🎂 <b>Возраст</b>\n"
        "Выберите режим фильтрации по возрасту:",
        reply_markup=make_age_filter_keyboard(current_mode)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("age_mode_"), ShowProfiles.filter_menu)
async def set_age_mode(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    mode = callback.data.split("age_mode_")[1]

    data = await state.get_data()
    filters = data.get('filters', {})

    if mode == 'all':
        if 'age_mode' in filters:
            del filters['age_mode']
            logger.info("Пользователь ID=%s сбросил фильтр возраста", user_id)
    else:
        filters['age_mode'] = mode
        logger.info("Пользователь ID=%s установил фильтр возраста: %s", user_id, mode)

    await state.update_data(filters=filters)

    await callback.message.edit_reply_markup(reply_markup=make_age_filter_keyboard(mode))
    await callback.answer(f"Режим установлен: {mode}")


@router.callback_query(F.data == "back_from_age_filter", ShowProfiles.filter_menu)
async def back_from_age_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s вернулся в меню фильтров из настройки возраста", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await callback.answer()


@router.callback_query(F.data == "set_filter_experience", ShowProfiles.filter_menu)
async def start_set_experience_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра опыта выступлений", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    selected = filters.get('experience', [])

    keyboard = make_experience_filter_keyboard(selected)

    await callback.message.edit_text(
        "🎙️ <b>Опыт выступлений</b>\n"
        "Выберите требуемый опыт (можно несколько):",
        reply_markup=keyboard
    )
    await state.set_state(ShowProfiles.filter_experience)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_exp_"), ShowProfiles.filter_experience)
async def toggle_experience_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    experience_name = callback.data.split("filter_exp_")[1]

    data = await state.get_data()
    filters = data.get('filters', {})
    selected_experiences = filters.get('experience', [])

    action = "добавил"
    if experience_name in selected_experiences:
        selected_experiences.remove(experience_name)
        action = "удалил"
    else:
        selected_experiences.append(experience_name)

    logger.info("Пользователь ID=%s %s опыт '%s' в фильтр", user_id, action, experience_name)

    filters['experience'] = selected_experiences
    await state.update_data(filters=filters)

    keyboard = make_experience_filter_keyboard(selected_experiences)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "reset_filter_experience", ShowProfiles.filter_experience)
async def reset_experience_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    if 'experience' in filters:
        del filters['experience']
        await state.update_data(filters=filters)
        logger.info("Пользователь ID=%s сбросил фильтр опыта выступлений", user_id)

    keyboard = make_experience_filter_keyboard([])

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer("Фильтр опыта сброшен")


@router.callback_query(F.data == "done_filter_experience", ShowProfiles.filter_experience)
async def done_experience_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    experience_count = len(filters.get('experience', []))
    logger.info("Пользователь ID=%s сохранил фильтр опыта выступлений (всего %d)", user_id, experience_count)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Опыт выступлений сохранен!")


@router.callback_query(F.data == "exit_filters_menu", ShowProfiles.filter_menu)
async def exit_filters_and_show(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    previous_state = data.get('previous_show_state', ShowProfiles.show_profiles)
    await state.set_state(previous_state)
    await callback.message.delete()

    await callback.message.answer(
        "✅ <b>Фильтры применены!</b>\nНажмите «Следующая анкета», чтобы продолжить.",
        reply_markup=show_reply_keyboard_for_registered_users()
    )
    logger.info("Пользователь ID=%s вышел из меню фильтров и применил их", user_id)

    await callback.answer()


@router.callback_query(F.data == "set_filter_level", ShowProfiles.filter_menu)
async def start_set_level_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра теоретических знаний", user_id)
    data = await state.get_data()
    filters = data.get('filters', {})
    current_level = filters.get('min_level')

    await callback.message.edit_text(
        "🧠 <b>Теоретические знания</b>\n"
        "Выберите <b>минимальный</b> уровень:\n"
        "<i>(Будут показаны анкеты с этим уровнем и выше)</i>",
        reply_markup=make_level_filter_keyboard(current_level)
    )

    await state.set_state(ShowProfiles.filter_level)
    await callback.answer()


@router.callback_query(F.data.startswith("level_val_"), ShowProfiles.filter_level)
async def set_level_value(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    level = int(callback.data.split("_")[2])

    data = await state.get_data()
    filters = data.get('filters', {})

    filters['min_level'] = level
    await state.update_data(filters=filters)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    logger.info("Пользователь ID=%s установил минимальный уровень знаний: %d", user_id, level)
    await callback.answer(f"Установлен мин. уровень: {level}")


@router.callback_query(F.data == "reset_filter_level", ShowProfiles.filter_level)
async def reset_level_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    if 'min_level' in filters:
        del filters['min_level']
        await state.update_data(filters=filters)
        logger.info("Пользователь ID=%s сбросил фильтр минимального уровня знаний", user_id)

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Фильтр уровня сброшен")


@router.callback_query(F.data == "back_from_level_filter", ShowProfiles.filter_level)
async def back_from_level_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('filters', {})

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров.</b> Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    logger.info("Пользователь ID=%s вернулся в меню фильтров из настройки уровня знаний", user_id)
    await callback.answer()


@router.message(F.text == "Вернуться на главную")
async def back_to_main_menu_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("Пользователь ID=%s нажал кнопку 'Вернуться на главную' (текст)", user_id)
    await start(message, state)


# 1. Открытие меню (работает по кнопке "Фильтр 🔍" когда мы в режиме show_bands)
@router.message(F.text == "Фильтр 🔍", ShowProfiles.show_bands)
async def open_group_filter_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Берем именно group_filters
    current_filters = data.get('group_filters', {})

    await message.answer(
        "⚙️ <b>Настройка фильтров групп.</b>\nЧто ищем?",
        reply_markup=get_group_filter_menu_keyboard(current_filters)
    )
    # Можно использовать то же состояние filter_menu или создать новое
    # Для чистоты создадим под-состояние (нужно добавить в класс ShowProfiles)
    # Но чтобы не ломать твой код, используем существующее, но с флагом в callback
    await state.set_state(ShowProfiles.filter_menu)


# 2. Выход из меню фильтров ГРУПП
@router.callback_query(F.data == "exit_group_filters_menu", ShowProfiles.filter_menu)
async def exit_group_filters(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ShowProfiles.show_bands)
    await callback.message.delete()
    await callback.message.answer(
        "✅ <b>Фильтры групп применены!</b>\nЖмите «Следующая анкета».",
        reply_markup=show_reply_keyboard_for_registered_users()
    )
    await callback.answer()


# 3. Сброс фильтров
@router.callback_query(F.data == "reset_group_filters", ShowProfiles.filter_menu)
async def reset_group_filters(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(group_filters={})
    await callback.message.edit_text(
        "🧹 <b>Фильтры групп сброшены.</b>",
        reply_markup=get_group_filter_menu_keyboard({})
    )
    await callback.answer()


# 4. Настройка Уровня Серьезности
@router.callback_query(F.data == "set_group_filter_level", ShowProfiles.filter_menu)
async def set_group_level(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters = data.get('group_filters', {})

    # ПРЕДПОЛОЖЕНИЕ: Получаем список коротких имен (names),
    # а не длинных значений (values)
    selected_names = filters.get('seriousness_level_names', [])

    await callback.message.edit_text(
        "📊 <b>Уровень группы</b>\nВыберите подходящие:",
        # Передаем список коротких имен
        reply_markup=make_seriousness_filter_keyboard(selected_names)
    )
    await state.set_state(ShowProfiles.filter_group_level)
    await callback.answer()


@router.callback_query(F.data.startswith("fgl_"), ShowProfiles.filter_group_level)
async def toggle_group_level(callback: types.CallbackQuery, state: FSMContext):
    # level_name = 'hobby', 'pro', etc.
    level_name = callback.data.split("fgl_")[1].upper()  # <--- Получаем короткое имя в ВЕРХНЕМ РЕГИСТРЕ

    data = await state.get_data()
    filters = data.get('group_filters', {})

    # ⚠️ Изменяем ключ в FSM, чтобы хранить короткие имена.
    # Это предотвратит путаницу со старыми длинными значениями.
    selected = filters.get('seriousness_level_names', [])  # Используем новый ключ

    if level_name in selected:
        selected.remove(level_name)
    else:
        selected.append(level_name)

    # Сохраняем короткие имена обратно в FSM
    filters['seriousness_level_names'] = selected
    await state.update_data(group_filters=filters)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(
            # Передаем список коротких имен
            reply_markup=make_seriousness_filter_keyboard(selected)
        )
    await callback.answer()


@router.callback_query(F.data == "done_group_filter_level", ShowProfiles.filter_group_level)
async def done_group_level(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters = data.get('group_filters', {})

    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров групп.</b>",
        reply_markup=get_group_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer()


# 5. Настройка Городов и Жанров (Повторное использование логики)
# Мы можем переиспользовать существующие функции make_city_filter_keyboard,
# но нужно сохранять данные именно в group_filters.

@router.callback_query(F.data == "set_group_filter_city", ShowProfiles.filter_menu)
async def set_group_city(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters = data.get('group_filters', {})
    selected = filters.get('cities', [])

    await callback.message.edit_text(
        "🏙️ <b>Города поиска групп</b>",
        reply_markup=make_city_filter_keyboard(selected)  # Переиспользуем твою клавиатуру
    )
    # Важно: используем ОТДЕЛЬНОЕ состояние, чтобы хендлер обработки клика понял,
    # что мы редактируем именно фильтр ГРУПП, а не юзеров.
    await state.set_state(ShowProfiles.filter_group_city)
    await callback.answer()


# Обработчик клика по городу для ГРУПП
@router.callback_query(F.data.startswith("filter_city_"), ShowProfiles.filter_group_city)
async def toggle_group_city(callback: types.CallbackQuery, state: FSMContext):
    # Логика 1 в 1 как у юзеров, но сохраняем в group_filters
    city_name = callback.data.split("filter_city_")[1]
    if city_name == "custom_prompt": return  # Обработка кастома отдельно

    data = await state.get_data()
    filters = data.get('group_filters', {})
    selected = filters.get('cities', [])

    if city_name in selected:
        selected.remove(city_name)
    else:
        selected.append(city_name)

    filters['cities'] = selected
    await state.update_data(group_filters=filters)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(
            reply_markup=make_city_filter_keyboard(selected)
        )
    await callback.answer()


@router.callback_query(F.data == "done_filter_city", ShowProfiles.filter_group_city)
async def done_group_city(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters = data.get('group_filters', {})
    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров групп.</b>",
        reply_markup=get_group_filter_menu_keyboard(filters)
    )
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer()


@router.callback_query(F.data == "set_group_filter_genres", ShowProfiles.filter_menu)
async def start_set_group_genres_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s перешел к настройке фильтра жанров ГРУПП", user_id)

    data = await state.get_data()
    filters = data.get('group_filters', {})
    selected = filters.get('genres', [])

    # Используем ту же клавиатуру, что и для юзеров, она универсальна
    keyboard = make_genre_filter_keyboard(selected)

    await callback.message.edit_text(
        "🎶 <b>Жанры групп</b>\n"
        "Выберите жанры, которые играют группы:",
        reply_markup=keyboard
    )
    # Устанавливаем специальное состояние для ГРУПП
    await state.set_state(ShowProfiles.filter_group_genres)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_genre_"), ShowProfiles.filter_group_genres)
async def toggle_group_genre_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Если нажали "Свой вариант" — пропускаем, это обработает следующий хендлер
    if callback.data == "filter_genre_custom_prompt":
        return

    genre_name = callback.data.split("filter_genre_")[1]

    data = await state.get_data()
    filters = data.get('group_filters', {})
    selected_genres = filters.get('genres', [])

    action = "добавил"
    if genre_name in selected_genres:
        selected_genres.remove(genre_name)
        action = "удалил"
    else:
        selected_genres.append(genre_name)

    logger.info("Пользователь ID=%s %s жанр '%s' в фильтр ГРУПП", user_id, action, genre_name)

    filters['genres'] = selected_genres
    await state.update_data(group_filters=filters)

    keyboard = make_genre_filter_keyboard(selected_genres)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "filter_genre_custom_prompt", ShowProfiles.filter_group_genres)
async def prompt_custom_group_genre(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь ID=%s запросил ввод кастомного жанра для фильтра ГРУПП", user_id)

    await callback.message.edit_text("📝 <b>Введите название жанра</b>, который вы ищете у групп:")
    # Специальное состояние для ввода текста
    await state.set_state(ShowProfiles.filter_group_genres_custom)
    await callback.answer()


@router.message(ShowProfiles.filter_group_genres_custom)
async def save_custom_group_genre_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_genre = message.text.strip()

    if not new_genre:
        await message.answer("⚠️ Пожалуйста, введите название жанра.")
        return

    # Ограничение длины, чтобы не ломать клавиатуру
    if len(new_genre) > 30:
        await message.answer("⚠️ Название жанра слишком длинное (макс 30 символов).")
        return

    data = await state.get_data()
    filters = data.get('group_filters', {})
    selected_genres = filters.get('genres', [])

    if new_genre not in selected_genres:
        selected_genres.append(new_genre)
        filters['genres'] = selected_genres
        await state.update_data(group_filters=filters)
        logger.info("Пользователь ID=%s добавил кастомный жанр '%s' в фильтр ГРУПП", user_id, new_genre)

    keyboard = make_genre_filter_keyboard(selected_genres)

    await message.answer(
        f"✅ Жанр <b>{new_genre}</b> добавлен в фильтр групп.\nВыберите еще или нажмите 'Готово'.",
        reply_markup=keyboard
    )
    # Возвращаем состояние выбора (кликов по кнопкам)
    await state.set_state(ShowProfiles.filter_group_genres)


@router.callback_query(F.data == "done_filter_genres", ShowProfiles.filter_group_genres)
async def done_group_genre_filter(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    filters = data.get('group_filters', {})

    genres_count = len(filters.get('genres', []))
    logger.info("Пользователь ID=%s сохранил фильтр жанров ГРУПП (всего %d)", user_id, genres_count)

    # Возвращаемся в главное меню фильтров ГРУПП
    await callback.message.edit_text(
        "⚙️ <b>Настройка фильтров групп.</b>\nЧто ищем?",
        reply_markup=get_group_filter_menu_keyboard(filters)
    )
    # Возвращаем состояние главного меню фильтров
    await state.set_state(ShowProfiles.filter_menu)
    await callback.answer("Жанры групп сохранены!")