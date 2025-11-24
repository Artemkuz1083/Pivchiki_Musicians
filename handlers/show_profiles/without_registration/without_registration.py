
import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.queries import get_random_profile, get_random_group
from handlers.show_profiles.without_registration.without_regist_kb import choose_keyboard_for_show, show_reply_keyboard
from handlers.start import start
from states.states_show_without_registration import ShowWithoutRegistration

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "show_without_registration")
async def start_show(callback: types.CallbackQuery, state: FSMContext):

    logger.info("Пользователь начал просмотр анкет без регистрации")

    msg = "Выберите, что вы хотите смотреть:"

    await callback.message.answer(text=msg, reply_markup=choose_keyboard_for_show())
    await state.set_state(ShowWithoutRegistration.choose)
    await callback.answer()

# выбор, что хочет смотреть пользователь
@router.callback_query(F.data.startswith("chs_"), ShowWithoutRegistration.choose)
async def choose_user(callback: types.CallbackQuery, state: FSMContext):
    choose = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await state.update_data(user_id=user_id)

    if choose == "bands":
        logger.info("Пользователь выбрал просмотр групп")
        await state.set_state(ShowWithoutRegistration.show_bands)
        await show_bands(callback.message, state)

    if choose == "artist":
        logger.info("Пользователь выбрал просмотр соло артистов")
        await state.set_state(ShowWithoutRegistration.show_profiles)
        await show_profiles(callback.message, state)

    await callback.answer()

# показывает анкеты групп
@router.message(F.text.startswith("Следующая анкета"), ShowWithoutRegistration.show_bands)
async def show_bands(message: types.Message, state: FSMContext):
    band = await get_random_group()

    name = band.name if band.name is not None else "Не указано"
    year = band.formation_date if band.formation_date is not None else "Не указано"
    genres = band.genres if band.genres is not None else "Не указано"
    city = band.city if band.city is not None else "Не указано"

    genres_display = ", ".join(genres)

    profile_text = (
        f"Название: {name} \n"
        f"Город: {city} \n"
        f"Год основания: {year}\n"
        f"Жанры: {genres_display}\n"
        "Хотите видеть больше информации о группах?\n"
        "Тогда пройдите регистрацию!\n"
        "Больше информации по кнопке \"Подробнее\"."
    )

    await message.answer(text=profile_text, reply_markup=show_reply_keyboard())

# показывает анкеты пользователей
@router.message(F.text.startswith("Следующая анкета"), ShowWithoutRegistration.show_profiles)
async def show_profiles(message: types.Message, state: FSMContext):
    logger.info("Пользователь нажал кнопку Следующая анкета")
    data = await state.get_data()
    user_id = data.get("user_id")

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

    base_info = (
        f"Имя: {user.name or 'Не указано'}\n"
        f"Город: {user.city or 'Не указано'}\n"
        f"Жанры: {genres_display}\n"
        f"Инструменты: \n{instruments_display}\n"
        "Хотите видеть больше информации об артистах?\n"
        "Тогда пройдите регистрацию!\n"
        "Больше информации по кнопке \"Подробнее\"."
    )

    await message.answer(text=base_info, reply_markup=show_reply_keyboard())

# возврат в главное меню
@router.message(F.text.startswith("Вернуться на главную"),ShowWithoutRegistration.show_bands)
@router.message(F.text.startswith("Вернуться на главную"),ShowWithoutRegistration.show_profiles)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await start(message, state)

# обработка кнопки "Подробнее"
@router.message(F.text.startswith("Подробнее"), ShowWithoutRegistration.show_bands)
@router.message(F.text.startswith("Подробнее"), ShowWithoutRegistration.show_profiles)
async def info(message: types.Message, state: FSMContext):
    logger.info("Пользователь нажал кнопку подробнее")
    msg = (
        "Понравилась анкета? Чтобы ставить лайки, надо пройти регистрацию!\n\n"
        "Также после регистрации вы сможете видеть:\n"
        "• Опыт выступлений\n"
        "• Информацию о себе\n"
        "• Аудио файлы музыкантов\n"
        "• И многое другое!"
    )

    await message.answer(text=msg, reply_markup=show_reply_keyboard())

def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level