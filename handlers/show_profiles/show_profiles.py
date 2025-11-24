
import logging
from xml.dom.domreg import registered

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.queries import get_random_profile, get_random_group
from handlers.show_profiles.show_keyboards import choose_keyboard_for_show, \
    show_reply_keyboard_for_unregistered_users, show_reply_keyboard_for_registered_users
from handlers.start import start
from main import bot
from states.states_show_profiles import ShowProfiles

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

    await state.update_data(user_id=user_id)

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

    profile_msg = ""

    try:
        logger.info("Пробуем получить данные о группе")
        band = await get_random_group()
    except Exception as e:
        logger.exception("Не получилось получить данные о группе")

    name = band.name if band.name is not None else "Не указано"
    year = band.formation_date if band.formation_date is not None else "Не указано"
    genres = band.genres if band.genres is not None else "Не указано"
    city = band.city if band.city is not None else "Не указано"

    genres_display = ", ".join(genres)

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
            f"Жанры: {genres}\n"
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

    profile_msg = ""

    try:
        logger.info("Пробуем получить рандомный профиль пользователя")
        user = await get_random_profile(user_id)
    except Exception as e:
        logger.exception("Ошибка при получении анкеты")
        return

    genres_list = user.genres or ["Не указано"]
    genres_display = ", ".join(genres_list)

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
    logger.info("Пользователь нажал кнопку лайк")
    data = await state.get_data()
    registered = data.get("registered")
    if not registered:
        return
    await message.answer("Вы оценили анкету")

    #TODO сделать запрос в бд

def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level