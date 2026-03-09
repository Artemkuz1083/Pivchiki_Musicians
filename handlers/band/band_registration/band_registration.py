import datetime
import html
import logging

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.queries import create_group
from handlers.band.band_registration.band_registration_states import BandRegistrationStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.enums.cities import City
from handlers.enums.seriousness_level import SeriousnessLevel
from handlers.profile.profile_keyboards import make_keyboard_for_genre
from handlers.registration.registration import logger  # Используем существующий логгер
from utils.analytics import track_event

router = Router()


async def _start_group_registration_logic(callback_or_message: types.CallbackQuery | types.Message, state: FSMContext):
    """Общая логика начала регистрации группы."""
    user_id: int
    chat_id: int

    if isinstance(callback_or_message, types.CallbackQuery):
        await callback_or_message.answer()
        user_id = callback_or_message.from_user.id
        chat_id = callback_or_message.message.chat.id
    else:
        user_id = callback_or_message.from_user.id
        chat_id = callback_or_message.chat.id

    await track_event(user_id, "band_registration_started")
    logger.info("Пользователь %s начал регистрацию группы", user_id)

    await callback_or_message.bot.send_message(
        chat_id=chat_id,
        text=(
            "🎸 <b>Регистрация группы</b>\n\n"
            "Давайте создадим профиль вашего коллектива.\n"
            "<b>Напишите название вашей группы:</b>"
        ),
        parse_mode='HTML',
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.update_data(user_id=user_id)
    await state.set_state(BandRegistrationStates.filling_name)


# если пользователь вдруг заново нажмет /start при регистрации
@router.message(F.text.startswith("/"), BandRegistrationStates.filling_name)
@router.message(F.text.startswith("/"), BandRegistrationStates.filling_foundation_date)
@router.message(F.text.startswith("/"), BandRegistrationStates.selecting_genres)
@router.message(F.text.startswith("/"), BandRegistrationStates.filling_own_genre)
async def block_commands_during_registration(message: types.Message):
    logger.warning("Пользователь %s пытался использовать команду во время регистрации в состоянии %s",
                   message.from_user.id, await message.state.get_state())
    await message.answer("⚠️ <b>Пожалуйста, закончите регистрацию, чтобы выйти в главное меню.</b>", parse_mode="HTML")
    return


@router.message(F.text == "🎸 Зарегистрировать группу")
async def start_group_registration_from_text(message: types.Message, state: FSMContext):
    """Ловит текстовое сообщение 'Зарегистрировать группу' от Reply-клавиатуры."""
    await _start_group_registration_logic(message, state)


@router.callback_query(F.data == "start_band_registration")
async def start_group_registration_from_callback(callback: types.CallbackQuery, state: FSMContext):
    """Ловит нажатие ИНЛАЙН-КНОПКИ для начала регистрации группы."""
    await _start_group_registration_logic(callback, state)


@router.message(F.text, BandRegistrationStates.filling_name)
async def process_group_name(message: types.Message, state: FSMContext):
    """Получает название группы и запрашивает год основания."""
    user_id = message.from_user.id
    group_name = message.text.strip()

    if len(group_name) > 100:
        logger.warning("Пользователь %s ввел слишком длинное название группы: %s", user_id, group_name)
        await message.answer("⚠️ Название группы слишком длинное (макс. 100 символов). Введите короче.")
        return

    await state.update_data(group_name=group_name)
    logger.info("Пользователь %s ввел название группы: %s", user_id, group_name)

    await message.answer(
        f"✅ Отличное название: <b>{html.escape(group_name)}</b>\n\n"
        "📅 Теперь укажите <b>год основания группы</b>.\n"
        "<i>Формат: ГГГГ (например, 2020).</i>",
        parse_mode='HTML'
    )

    await state.set_state(BandRegistrationStates.filling_foundation_date)


@router.message(F.text, BandRegistrationStates.filling_foundation_date)
async def process_foundation_date(message: types.Message, state: FSMContext):
    """Получает год основания и переходит к выбору жанров."""
    user_id = message.from_user.id
    year_text = message.text.strip()
    current_year = datetime.datetime.now().year

    if not year_text.isdigit():
        logger.warning("Пользователь %s ввел нечисловой год основания: %s", user_id, year_text)
        await message.answer("⚠️ Введите год только цифрами (например, 2018).")
        return

    year = int(year_text)

    if year < 1900 or year > current_year:
        logger.warning("Пользователь %s ввел некорректный год основания: %d", user_id, year)
        await message.answer(
            f"⚠️ Год должен быть от 1900 до {current_year}.\nПожалуйста, введите корректный год (ГГГГ)."
        )
        return

    # Сохраняем год как строку
    await state.update_data(foundation_year=year_text)
    logger.info("Пользователь %s ввел год основания группы: %s", user_id, year_text)

    # Переход к выбору жанров
    await state.update_data(user_choice_genre=[], own_user_genre=[])
    markup = make_keyboard_for_genre([])

    await message.answer(
        "🎶 Почти готово! Теперь <b>выберите жанры</b>, в которых играет ваша группа.",
        reply_markup=markup,
        parse_mode='HTML'
    )

    await state.set_state(BandRegistrationStates.selecting_genres)


@router.callback_query(F.data.startswith("genre_"), BandRegistrationStates.selecting_genres)
async def choose_group_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров группы."""
    user_id = callback.from_user.id
    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        logger.info("Пользователь %s выбрал ввод собственного жанра для группы", user_id)
        await callback.message.edit_text(text="📝 <b>Напишите название жанра:</b>", parse_mode="HTML")
        await state.set_state(BandRegistrationStates.filling_own_genre)
        return

    action = ""
    if choose in user_choice:
        user_choice.remove(choose)
        action = "удалил"
    else:
        user_choice.append(choose)
        action = "добавил"

    logger.info("Пользователь %s %s жанр: %s", user_id, action, choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_genre(user_choice)
    )
    await state.update_data(user_choice_genre=user_choice)


@router.message(F.text, BandRegistrationStates.filling_own_genre)
async def own_group_genre(message: types.Message, state: FSMContext):
    """Обработка кнопки свой вариант для жанров группы."""
    user_id = message.from_user.id
    new_genre = message.text.strip()

    if new_genre.startswith('/'):
        logger.warning("Пользователь %s пытался ввести жанр, начинающийся с команды: %s", user_id, new_genre)
        await message.answer("⚠️ Название жанра не может начинаться с '/'.\n<b>Напишите жанр:</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)  # Сохраняем собственный жанр
    logger.info("Пользователь %s добавил собственный жанр для группы: %s", user_id, new_genre)

    formatted_own = ", ".join([f"<i>{html.escape(g)}</i>" for g in own_user_genre])

    msg_text = (f"✅ Свой вариант добавлен: {formatted_own}\n\n"
                "<b>Выберите еще жанры или нажмите 'Готово':</b>")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice), parse_mode="HTML")
    await state.set_state(BandRegistrationStates.selecting_genres)


@router.callback_query(F.data == "done_genres", BandRegistrationStates.selecting_genres)
async def done_group_genres(callback: types.CallbackQuery, state: FSMContext):
    """Сохраняет жанры и переходит к выбору города."""
    user_id = callback.from_user.id
    data = await state.get_data()
    all_genres_user = data.get("user_choice_genre", []) + data.get("own_user_genre", [])

    if len(all_genres_user) == 0:
        logger.warning("Пользователь %s попытался завершить выбор жанров без выбора", user_id)
        await callback.answer("⚠️ Выберите хотя бы один жанр!", show_alert=True)
        return

    await state.update_data(genres=all_genres_user)
    logger.info("Пользователь %s сохранил жанры группы: %s", user_id, all_genres_user)

    markup = make_keyboard_for_city(None)

    await callback.message.edit_text(
        "🏙 <b>Отлично!</b>\nТеперь выберите город, в котором базируется ваша группа:",
        reply_markup=markup,
        parse_mode='HTML'
    )

    await state.set_state(BandRegistrationStates.selecting_city)


def make_keyboard_for_city(selected_city: str | None = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру городов с подсветкой выбранного города."""
    builder = InlineKeyboardBuilder()
    available_cities = City.list_values()

    for city in available_cities:
        text = f"✅ {city}" if city == selected_city else city
        builder.add(InlineKeyboardButton(text=text, callback_data=f"city_{city}"))

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="Свой вариант 📝", callback_data="city_Свой вариант"))
    builder.row(InlineKeyboardButton(text="➡️ Готово", callback_data="done_city"))

    return builder.as_markup()


@router.callback_query(F.data.startswith("city_"), BandRegistrationStates.selecting_city)
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    city = callback.data.split("_")[1]

    if city == 'Свой вариант':
        logger.info("Пользователь %s выбрал ввод собственного города для группы", user_id)
        back_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="done_genres")]])

        await callback.message.edit_text(
            text="📝 <b>Напишите город, в котором базируется ваша группа:</b>",
            reply_markup=back_markup,
            parse_mode="HTML"
        )
        await state.set_state(BandRegistrationStates.filling_own_city)
        await callback.answer()
        return

    await state.update_data(city=city)
    logger.info("Пользователь %s выбрал стандартный город для группы: %s", user_id, city)
    markup = make_keyboard_for_city(city)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(f"✅ Город '{city}' выбран!")


@router.message(F.text, BandRegistrationStates.filling_own_city)
async def process_own_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text.strip()

    if city.startswith('/'):
        logger.warning("Пользователь %s пытался ввести город, начинающийся с команды: %s", user_id, city)
        await message.answer("⚠️ Название города не может начинаться с '/'.\n<b>Напишите город:</b>", parse_mode="HTML")
        return

    await state.update_data(city=city)
    logger.info("Пользователь %s ввел собственный город для группы: %s", user_id, city)
    markup = make_keyboard_for_city(city)

    await message.answer(
        f"✅ Город <b>{html.escape(city)}</b> сохранен.\nНажмите 'Готово', чтобы продолжить.",
        reply_markup=markup,
        parse_mode="HTML"
    )

    await state.set_state(BandRegistrationStates.selecting_city)


@router.callback_query(F.data == "done_city", BandRegistrationStates.selecting_city)
async def done_city_and_start_description(callback: types.CallbackQuery, state: FSMContext):
    """Проверяет город и переводит к вводу описания 'О себе'."""
    user_id = callback.from_user.id
    data = await state.get_data()
    await callback.answer()

    city = data.get("city")
    if not city:
        logger.warning("Пользователь %s попытался пропустить выбор города", user_id)
        await callback.answer("⚠️ Выберите город или введите свой вариант!", show_alert=True)
        return

    logger.info("Пользователь %s подтвердил город: %s. Переход к описанию.", user_id, city)

    skip_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="➡️ Пропустить", callback_data="skip_description")]]
    )

    await callback.message.edit_text(
        "📝 <b>Последний шаг!</b>\n\n"
        "Напишите немного о вашей группе (стиль, достижения, идеи, цели).\n"
        "<i>Максимум 1024 символа.</i>",
        reply_markup=skip_markup,
        parse_mode='HTML'
    )

    await state.set_state(BandRegistrationStates.filling_description)


@router.message(F.text, BandRegistrationStates.filling_description)
async def process_description_and_continue(message: types.Message, state: FSMContext):
    """Получает описание 'О себе' и переходит к выбору уровня."""
    user_id = message.from_user.id
    description = message.text.strip()

    if len(description) > 1024:
        logger.warning("Пользователь %s ввел слишком длинное описание группы", user_id)
        await message.answer("⚠️ Описание слишком длинное (максимум 1024 символа). Пожалуйста, сократите текст.")
        return

    await state.update_data(description=description)
    logger.info("Пользователь %s ввел описание группы. Длина: %d", user_id, len(description))

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Не удалось удалить сообщение пользователя %s при вводе описания: %s", user_id, e)
        pass

    await message.answer(
        "✅ Описание сохранено!\n\n📊 <b>Выберите уровень серьезности вашей группы:</b>",
        reply_markup=make_keyboard_for_level(),
        parse_mode='HTML'
    )
    await state.set_state(BandRegistrationStates.selecting_seriousness_level)


@router.callback_query(F.data == "skip_description", BandRegistrationStates.filling_description)
async def skip_description_and_continue(callback: types.CallbackQuery, state: FSMContext):
    """Пропускает ввод описания и переходит к выбору уровня."""
    user_id = callback.from_user.id
    logger.info("Пользователь %s пропустил ввод описания группы", user_id)

    await callback.answer("Описание пропущено.")
    await state.update_data(description=None)

    await callback.message.edit_text(
        "📊 <b>Выберите уровень серьезности вашей группы:</b>",
        reply_markup=make_keyboard_for_level(),
        parse_mode='HTML'
    )
    await state.set_state(BandRegistrationStates.selecting_seriousness_level)


def make_keyboard_for_level() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора уровня серьезности."""
    builder = InlineKeyboardBuilder()

    for level in SeriousnessLevel:
        builder.add(InlineKeyboardButton(
            text=level.value,
            callback_data=f"level_{level.name}"
        ))

    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("level_"), BandRegistrationStates.selecting_seriousness_level)
async def process_level_and_finish(callback: types.CallbackQuery, state: FSMContext):
    """Получает ключ уровня, находит значение в Enum и сохраняет."""
    user_id = callback.from_user.id
    level_name = callback.data.split("_", 1)[1]

    try:
        selected_level = SeriousnessLevel[level_name]
    except KeyError:
        logger.error("Пользователь %s выбрал неверный уровень серьезности: %s", user_id, level_name)
        await callback.answer("⚠️ Неверный выбор уровня.")
        return

    await state.update_data(seriousness_level=selected_level.value)
    logger.info("Пользователь %s выбрал уровень серьезности: %s", user_id, selected_level.value)

    await callback.answer(f"✅ Уровень выбран!")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning("Не удалось удалить клавиатуру после выбора уровня для %s: %s", user_id, e)
        pass

    await _save_band_and_finish(callback, user_id, state)


async def _save_band_and_finish(source: types.Message | types.CallbackQuery, user_id: int, state: FSMContext):
    """
    Собирает все данные из FSM, сохраняет их в БД, отправляет профиль и очищает FSM.
    """
    data = await state.get_data()

    # Сборка данных для сохранения
    group_data = {
        "user_id": user_id,
        "name": data.get("group_name"),
        "foundation_year": data.get("foundation_year"),
        "genres": data.get("genres", []),
        "city": data.get("city"),
        "description": data.get("description"),
        "seriousness_level": data.get("seriousness_level")
    }

    try:
        await create_group(group_data)
        await track_event(user_id, "band_registration_success", {
            "city": data.get("city"),
            "level": data.get("seriousness_level"),
            "genre_count": len(data.get("genres", []))
        })
        logger.info("🎉 Группа успешно зарегистрирована для пользователя %s: %s. Данные: %s",
                    user_id, group_data['name'],
                    {k: v for k, v in group_data.items() if k not in ['user_id', 'description']})
    except Exception as e:
        logger.error("❌ Ошибка при регистрации группы для пользователя %s: %s. Данные: %s",
                     user_id, e, group_data['name'])

        message_source = source.message if isinstance(source, types.CallbackQuery) else source
        await message_source.answer("⚠️ Произошла ошибка при регистрации группы. Попробуйте позже.")
        await state.clear()
        return

    success_msg = f"🎉 <b>Поздравляем!</b> Группа <b>{html.escape(group_data['name'])}</b> успешно зарегистрирована!"

    await send_band_profile(source, user_id, success_message=success_msg)
    await state.clear()

    # Отправляем Reply-клавиатуру
    kb = [
        [types.KeyboardButton(text="👤 Моя анкета")],
        [types.KeyboardButton(text="🎸 Моя группа")],
        [types.KeyboardButton(text="🔍 Смотреть анкеты")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    message_source = source.message if isinstance(source, types.CallbackQuery) else source
    await message_source.answer("<b>Выберите действие:</b>", reply_markup=keyboard, parse_mode="HTML")