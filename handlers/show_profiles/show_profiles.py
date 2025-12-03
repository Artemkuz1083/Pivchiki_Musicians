import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.queries import get_random_profile, get_random_group, save_user_interaction, save_group_interaction
from handlers.show_profiles.show_keyboards import choose_keyboard_for_show, \
    show_reply_keyboard_for_unregistered_users, show_reply_keyboard_for_registered_users
from handlers.start import start
from main import bot
from states.states_show_profiles import ShowProfiles
from database.enums import Actions

from aiogram.fsm.state import default_state
from handlers.show_profiles.show_keyboards import get_filter_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()

# старт просмотр анкет, если пользователь не зарегистрирован
@router.callback_query(F.data == "show_without_registration")
async def start_show_unregistered_user(callback: types.CallbackQuery, state: FSMContext):

    logger.info("Пользователь начал просмотр анкет без регистрации")

    msg = "Выберите, что вы хотите смотреть:"

    await callback.message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.update_data(registered=False)
    await state.set_state(ShowProfiles.choose)
    await callback.answer()

# старт просмотр анкет, если пользователь зарегистрирован
@router.callback_query(F.data == "show_with_registration")
async def start_show_unregistered_user(callback: types.CallbackQuery, state: FSMContext):

    logger.info("Пользователь начал просмотр анкет c регистрацией")

    msg = "Выберите, что вы хотите смотреть:"

    await callback.message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.update_data(registered=True)
    await state.set_state(ShowProfiles.choose)
    await callback.answer()

# старт просмотр анкет, если пользователь зарегистрирован
@router.message(F.text.startswith("Смотреть анкеты"))
async def start_show_registered_user(message: types.Message, state: FSMContext):

    logger.info("Пользователь начал просмотр анкет c регистрацией")

    msg = "Выберите, что вы хотите смотреть:"

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
        logger.info("Пользователь выбрал просмотр групп")
        await state.set_state(ShowProfiles.show_bands)
        await show_bands(callback.message, state)

    if choose == "artist":
        logger.info("Пользователь выбрал просмотр соло артистов")
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

    prev_target_id = data.get("current_target_id")
    prev_target_type = data.get("current_target_type")

    if prev_target_id and prev_target_type == "group":
        # Если предыдущая цель была группой, записываем SKIP
        try:
            await save_group_interaction(user_id, prev_target_id, Actions.SKIP)
            logger.info(f"Записан автоматический SKIP: user {user_id} -> group {prev_target_id}")
        except Exception as e:
            logger.error(f"Ошибка при записи SKIP: {e}")

    profile_msg = ""

    try:
        logger.info("Пробуем получить данные о группе")
        band = await get_random_group(user_id)
        if not band:
            await message.answer("Анкеты групп закончились! Попробуйте позже.")
            await state.update_data(current_target_id=None, current_target_type=None)
            return
    except Exception as e:
        logger.exception("Не получилось получить данные о группе")

    await state.update_data(current_target_id=band.id, current_target_type="group")

    name = band.name if band.name is not None else "Не указано"
    year = band.formation_date if band.formation_date is not None else "Не указано"
    genres_list = band.genres = band.genres if band.genres is not None else "Не указано"
    city = band.city if band.city is not None else "Не указано"

    genre_names = [genre_entity.name for genre_entity in genres_list]
    genres_display = ", ".join(genre_names)

    if not registered:
        markup = show_reply_keyboard_for_unregistered_users()
        profile_msg = (
            f"Название: {name} \n"
            f"Город: {city} \n"
            f"Год основания: {year}\n"
            f"Жанры: {genres_display}\n"
            "Хотите видеть больше информации о группах?\n"
            "Тогда пройдите регистрацию!\n"
            "Больше информации по кнопке \"Подробнее\"."
        )

    if registered:
        markup = show_reply_keyboard_for_registered_users()
        description = band.description if band.description is not None else "Не указано"
        level = band.seriousness_level if band.seriousness_level is not None else "Не указано"

        profile_msg = (

            f"Название: {name}\n"
            f"Год основания: {year}\n"
            f"Город: {city}\n"
            f"Уровень: {level}\n"
            f"Жанры: {genre_names}\n"
            f"\n"
            f"О себе:\n"
            f"_{description}_\n"
            f"\n"
            "Выберите, что хотите изменить:"
        )

    await message.answer(text=profile_msg, reply_markup=markup)

# показывает анкеты пользователей
@router.message(F.text.startswith("Следующая анкета"), ShowProfiles.show_profiles)
async def show_profiles(message: types.Message, state: FSMContext):
    logger.info("Пользователь нажал кнопку Следующая анкета")
    data = await state.get_data()
    user_id = data.get("user_id")
    registered = data.get("registered")
    markup: types.ReplyKeyboardMarkup

    prev_target_id = data.get("current_target_id")
    prev_target_type = data.get("current_target_type")

    if prev_target_id and prev_target_type == "user":
        # Если предыдущая цель была пользователем, записываем SKIP
        try:
            await save_user_interaction(user_id, prev_target_id, Actions.SKIP)
            logger.info(f"Записан автоматический SKIP: user {user_id} -> user {prev_target_id}")
        except Exception as e:
            logger.error(f"Ошибка при записи SKIP: {e}")

    profile_msg = ""

    try:
        logger.info("Пробуем получить рандомный профиль пользователя")
        user = await get_random_profile(user_id)
        if not user:
            await message.answer("Анкеты пользователей закончились! Попробуйте позже.")
            await state.update_data(current_target_id=None, current_target_type=None)
            return
    except Exception as e:
        logger.exception("Ошибка при получении анкеты")
        return

    await state.update_data(current_target_id=user.id, current_target_type="user")

    genres_list = user.genres or ["Не указано"]
    genre_names = [genre_entity.name for genre_entity in genres_list]
    genres_display = ", ".join(genre_names)

    instruments_lines = []
    if user.instruments:
        for instrument in user.instruments:
            proficiency_level = instrument.proficiency_level if instrument.proficiency_level is not None else 0
            stars_proficiency = rating_to_stars(proficiency_level)
            # УБЕРАЕМ Markdown из строк с инструментами
            instruments_lines.append(
                f"  • {instrument.name}: {stars_proficiency}"  # убрал **
            )
        instruments_display = "\n".join(instruments_lines)
    else:
        instruments_display = "Не указаны"

    if not registered:
        profile_msg = (
            f"Имя: {user.name or 'Не указано'}\n"
            f"Город: {user.city or 'Не указано'}\n"
            f"Жанры: {genres_display}\n"
            f"Инструменты: \n{instruments_display}\n"
            "Хотите видеть больше информации об артистах?\n"
            "Тогда пройдите регистрацию!\n"
            "Больше информации по кнопке \"Подробнее\"."
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

        profile_msg = (
            f"Имя: {user.name or 'Не указано'}\n"
            f"Возраст: {user.age or 'Не указано'}\n"
            f"Город: {user.city or 'Не указано'}\n\n"

            f"О себе:\n"
            f"{about_me_display}\n\n"

            f"Уровень теоретических знаний: {stars_knowledge}\n"
            f"Опыт выступлений: {experience_display or 'Не указано'}\n\n"

            f"Внешняя ссылка: {external_link_display}\n\n"

            f"Любимые жанры: {genres_display}\n\n"

            f"Инструменты:\n"
            f"{instruments_display}\n\n"
        )

        if user.photo_path:
            try:
                # Отправляем фото по file_id
                await bot.send_photo(chat_id, photo=user.photo_path, caption="Фото профиля:")
            except Exception as e:
                # Если file_id устарел или неверен, отправляем уведомление
                logger.error("Ошибка отправки фото по file_id: %s", e)
                await bot.send_message(chat_id, "Фото профиля не удалось загрузить.")

        # Отправка Аудио
        if user.audio_path:
            try:
                await bot.send_audio(chat_id, audio=user.audio_path, caption="Демо-трек:")
            except Exception as e:
                logger.error("Ошибка отправки аудио по file_id: %s", e)
                await bot.send_message(chat_id, "Демо-трек не удалось загрузить.")


    await message.answer(text=profile_msg, reply_markup=markup)

# возврат в главное меню
@router.message(F.text.startswith("Вернуться на главную"), ShowProfiles.show_bands)
@router.message(F.text.startswith("Вернуться на главную"), ShowProfiles.show_profiles)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await start(message, state)

# обработка кнопки "Подробнее"
@router.message(F.text.startswith("Подробнее"), ShowProfiles.show_bands)
@router.message(F.text.startswith("Подробнее"), ShowProfiles.show_profiles)
async def info(message: types.Message, state: FSMContext):
    logger.info("Пользователь нажал кнопку подробнее")
    data = await state.get_data()
    registered = data.get("registered")
    if registered:
        return
    msg = (
        "Понравилась анкета? Чтобы ставить лайки, надо пройти регистрацию!\n\n"
        "Также после регистрации вы сможете видеть:\n"
        "• Опыт выступлений\n"
        "• Информацию о себе\n"
        "• Аудио файлы музыкантов\n"
        "• И многое другое!"
    )

    await message.answer(text=msg, reply_markup=show_reply_keyboard_for_unregistered_users())

# обработка лайка
@router.message(F.text.startswith("❤️"), ShowProfiles.show_bands)
@router.message(F.text.startswith("❤️"), ShowProfiles.show_profiles)
async def like(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    target_id = data.get("current_target_id")
    target_type = data.get("current_target_type")

    if not user_id or not target_id:
        return await message.answer("Не удалось определить текущую анкету. Нажмите 'Следующая анкета'.")

    if target_type == "user":
        await save_user_interaction(user_id, target_id, Actions.LIKE)

        await message.answer("вы оценили данного музыканта")
        # TODO: Здесь нужна логика отправки уведомлений другому пользователю


    elif target_type == "group":
        await save_group_interaction(user_id, target_id, Actions.LIKE)
        await message.answer("Вы оценили группу! Они увидят ваш интерес.")

    await state.update_data(current_target_id=None, current_target_type=None)

def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level



# 1. Хендлер открытия меню фильтров
@router.message(F.text == "Фильтр 🔍", (ShowProfiles.show_bands | ShowProfiles.show_profiles))
async def open_filter_menu(message: types.Message, state: FSMContext):
    logger.info("Пользователь открыл меню фильтров")

    data = await state.get_data()

    # Сохраняем текущее состояние просмотра, чтобы потом вернуться
    current_show_state = await state.get_state()
    await state.update_data(previous_show_state=current_show_state)

    # Получаем текущие фильтры (если они есть)
    current_filters = data.get('filters', {})

    await message.answer(
        "⚙️ Настройка фильтров. Ваши текущие параметры:",
        reply_markup=get_filter_menu_keyboard(current_filters)
    )
    await state.set_state(ShowProfiles.filter_menu)


# 2. Хендлер возврата из меню фильтров
@router.callback_query(F.data == "back_from_filters", ShowProfiles.filter_menu)
async def back_to_showing(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Восстанавливаем предыдущее состояние просмотра
    previous_state = data.get('previous_show_state', ShowProfiles.show_profiles)

    await state.set_state(previous_state)
    await callback.message.delete()

    # Отправляем сообщение, чтобы сработала Reply-клавиатура "Следующая анкета"
    # Это триггернет показ анкеты с новыми фильтрами
    await callback.message.answer(
        "Настройки фильтров применены.",
        reply_markup=show_reply_keyboard_for_registered_users()
    )
    await callback.answer("Фильтры сохранены!")


# 3. Хендлер сброса фильтров
@router.callback_query(F.data == "reset_filters", ShowProfiles.filter_menu)
async def reset_filters(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(filters={})

    await callback.message.edit_text(
        "🧹 Все фильтры сброшены до значений 'Все'.",
        reply_markup=get_filter_menu_keyboard({})  # Показываем обновленное меню
    )
    await callback.answer("Фильтры сброшены!")


# 4. Хендлер начала установки города
@router.callback_query(F.data == "set_filter_city", ShowProfiles.filter_menu)
async def start_set_city_filter(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🏙️ Введите город, в котором хотите искать анкеты, или '0', чтобы искать везде:"
    )
    await state.set_state(ShowProfiles.filter_city)
    await callback.answer()


# 5. Хендлер сохранения города
@router.message(ShowProfiles.filter_city)
async def save_city_filter(message: types.Message, state: FSMContext):
    city = message.text.strip()

    data = await state.get_data()
    filters = data.get('filters', {})

    if city == '0':
        if 'city' in filters:
            del filters['city']
        display_city = 'Все'
    else:
        filters['city'] = city
        display_city = city

    await state.update_data(filters=filters)

    await message.answer(
        f"✅ Фильтр по городу установлен: **{display_city}**",
        reply_markup=get_filter_menu_keyboard(filters)
    )
    # Возвращаемся в меню фильтров
    await state.set_state(ShowProfiles.filter_menu)