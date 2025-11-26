import datetime

from aiogram import F, types, Router, Bot, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.queries import create_group
from handlers.band.band_registration.band_registration_states import BandRegistrationStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.enums.cities import City
from handlers.enums.seriousness_level import SeriousnessLevel
from handlers.profile.profile_keyboards import make_keyboard_for_genre
from handlers.registration.registration import logger

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

    await callback_or_message.bot.send_message(
        chat_id=chat_id,
        text=(
            "**Начнем регистрацию группы**\n\n"
            "Напишите название вашей группы"
        ),
        parse_mode='Markdown',
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
    logger.warning("Пользователь %s пытался использовать команду во время регистрации", message.from_user.id)

    await message.answer("Закончите регистрацию, чтобы выйти в главное меню")
    return

@router.message(F.text == "Зарегистрировать группу")
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
    group_name = message.text

    if len(group_name) > 100:
        await message.answer("Название группы слишком длинное. Пожалуйста, введите название короче.")
        return

    await state.update_data(group_name=group_name)

    await message.answer(
        "Успех! Теперь укажите **год основания группы**.\n\n"
        "Формат: **ГГГГ** (например, 1993).",
        parse_mode='Markdown'
    )

    await state.set_state(BandRegistrationStates.filling_foundation_date)

@router.message(F.text, BandRegistrationStates.filling_foundation_date)
async def process_foundation_date(message: types.Message, state: FSMContext):
    """Получает год основания и переходит к выбору жанров."""
    year_text = message.text
    current_year = datetime.datetime.now().year

    if not year_text.isdigit():
        await message.answer("Введите год только цифрами (например, 2018).")
        return

    year = int(year_text)

    if year < 1950 or year > current_year:
        await message.answer(
            f"Год должен быть в диапазоне от 1950 до {current_year} (текущего года). Пожалуйста, введите корректный год (ГГГГ)."
        )
        return

    # Сохраняем год как строку
    await state.update_data(foundation_year=year_text)

    #Переход к выбору жанров
    await state.update_data(user_choice_genre=[], own_user_genre=[])

    markup = make_keyboard_for_genre([])

    await message.answer(
        "Почти готово! Теперь **выберите жанры**, в которых играет ваша группа.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

    await state.set_state(BandRegistrationStates.selecting_genres)

@router.callback_query(F.data.startswith("genre_"), BandRegistrationStates.selecting_genres)
async def choose_group_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров группы."""
    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        await callback.message.edit_text(text="Напишите жанр:")
        await state.set_state(BandRegistrationStates.filling_own_genre)
        return

    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_genre(user_choice)
    )
    await state.update_data(user_choice_genre=user_choice)

@router.message(F.text, BandRegistrationStates.filling_own_genre)
async def own_group_genre(message: types.Message, state: FSMContext):
    """Обработка кнопки свой вариант для жанров группы."""
    new_genre = message.text
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)  # Сохраняем собственный жанр

    msg_text = (f"Свой вариант: {', '.join(own_user_genre)}\n"
                "Отлично! Теперь выберите жанры в которых играет ваша группа:")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice))
    await state.set_state(BandRegistrationStates.selecting_genres)


@router.callback_query(F.data == "done_genres", BandRegistrationStates.selecting_genres)
async def done_group_genres(callback: types.CallbackQuery, state: FSMContext):
    """Сохраняет жанры и переходит к выбору города."""
    data = await state.get_data()

    all_genres_user = data.get("user_choice_genre", []) + data.get("own_user_genre", [])

    if len(all_genres_user) == 0:
        await callback.answer("Чтобы идти дальше обязательно выбрать хотя бы один жанр")
        return

    await state.update_data(genres=all_genres_user)

    markup = make_keyboard_for_city(None)

    # Редактируем сообщение, чтобы показать клавиатуру городов
    await callback.message.edit_text(
        "Спасибо за выбор жанров! Теперь **выберите город**, в котором базируется ваша группа:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

    await state.set_state(BandRegistrationStates.selecting_city)


def make_keyboard_for_city(selected_city: str | None = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру городов с подсветкой выбранного города."""
    builder = InlineKeyboardBuilder()
    available_cities = City.list_values()

    for city in available_cities:
        # Добавляем галочку, если город выбран
        text = f"✅ {city}" if city == selected_city else city

        builder.add(InlineKeyboardButton(text=text, callback_data=f"city_{city}"))

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="Свой вариант", callback_data="city_Свой вариант"))
    builder.row(InlineKeyboardButton(text="➡️ Готово", callback_data="done_city"))

    return builder.as_markup()

@router.callback_query(F.data.startswith("city_"), BandRegistrationStates.selecting_city)
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[1]
    if city == 'Свой вариант':
        back_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="done_genres")]])

        await callback.message.edit_text(
            text="Напишите город, в котором базируется ваша группа:",
            reply_markup=back_markup
        )
        await state.set_state(BandRegistrationStates.filling_own_city)
        await callback.answer()
        return

    await state.update_data(city=city)
    markup = make_keyboard_for_city(city)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(f"✅ Город '{city}' успешно выбран!")


@router.message(F.text, BandRegistrationStates.filling_own_city)
async def process_own_city(message: types.Message, state: FSMContext):
    city = message.text

    if city.startswith('/'):
        await message.answer(
            "Название города не может начинаться с '/'. Пожалуйста, введите корректное название города:")
        return

    await state.update_data(city=city)
    logger.info("Пользователь %s ввел собственный город для группы: %s", message.from_user.id, city)
    markup = make_keyboard_for_city(city)

    await message.answer(
        f"Город '{city}' сохранен. Нажмите 'Готово (Город)', чтобы завершить регистрацию.",
        reply_markup=markup
    )

    await state.set_state(BandRegistrationStates.selecting_city)


@router.callback_query(F.data == "done_city", BandRegistrationStates.selecting_city)
async def done_city_and_start_description(callback: types.CallbackQuery, state: FSMContext):
    """Проверяет город и переводит к вводу описания 'О себе'."""
    data = await state.get_data()
    await callback.answer()

    city = data.get("city")
    if not city:
        await callback.answer("Пожалуйста, выберите город или введите 'Свой вариант', чтобы продолжить.")
        return

    skip_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="➡️ Пропустить", callback_data="skip_description")]]
    )

    await callback.message.edit_text(
        "Последний шаг! **Напишите немного о вашей группе** (стиль, достижения, идеи, цели).\n\n"
        "Максимум 1024 символа.",
        reply_markup=skip_markup,
        parse_mode='Markdown'
    )

    await state.set_state(BandRegistrationStates.filling_description)


@router.message(F.text, BandRegistrationStates.filling_description)
async def process_description_and_continue(message: types.Message, state: FSMContext):
    """Получает описание 'О себе' и переходит к выбору уровня."""
    description = message.text
    if len(description) > 1024:
        await message.answer("Описание слишком длинное (максимум 1024 символа). Пожалуйста, сократите текст.")
        return
    await state.update_data(description=description)

    try:
        await message.delete()
    except:
        pass

    await message.answer(
        "Спасибо! Теперь **выберите уровень серьезности** вашей группы:",
        reply_markup=make_keyboard_for_level(),
        parse_mode='Markdown'
    )
    await state.set_state(BandRegistrationStates.selecting_seriousness_level)


@router.callback_query(F.data == "skip_description", BandRegistrationStates.filling_description)
async def skip_description_and_continue(callback: types.CallbackQuery, state: FSMContext):
    """Пропускает ввод описания и переходит к выбору уровня."""
    await callback.answer("Описание пропущено.")
    await state.update_data(description=None)

    await callback.message.edit_text(
        "Теперь **выберите уровень серьезности** вашей группы:",
        reply_markup=make_keyboard_for_level(),
        parse_mode='Markdown'
    )
    await state.set_state(BandRegistrationStates.selecting_seriousness_level)

@router.callback_query(F.data == "skip_description", BandRegistrationStates.filling_description)
async def skip_description_and_finish(callback: types.CallbackQuery, state: FSMContext):
    """Пропускает ввод описания, сохраняет все данные (с пустым description) в БД и завершает."""
    user_id = callback.from_user.id
    await callback.answer("Описание пропущено.")

    # Явно сохраняем description=None
    await state.update_data(description=None)
    await callback.message.edit_text(
        "Теперь **выберите уровень серьезности** вашей группы:",
        reply_markup=make_keyboard_for_level(),
        parse_mode='Markdown'
    )

    await _save_band_and_finish(callback, user_id, state)

def make_keyboard_for_level() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора уровня серьезности."""
    builder = InlineKeyboardBuilder()

    for level in SeriousnessLevel:
        builder.add(InlineKeyboardButton(
            text=level.value,               # Текст на кнопке: "Хобби (для души)"
            callback_data=f"level_{level.name}" # Данные: "level_HOBBY" (коротко и без ошибок)
        ))

    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("level_"), BandRegistrationStates.selecting_seriousness_level)
async def process_level_and_finish(callback: types.CallbackQuery, state: FSMContext):
    """Получает ключ уровня, находит значение в Enum и сохраняет."""
    level_name = callback.data.split("_", 1)[1]

    try:
        selected_level = SeriousnessLevel[level_name]
    except KeyError:
        await callback.answer("Неверный выбор уровня.")
        return

    await state.update_data(seriousness_level=selected_level.value)
    user_id = callback.from_user.id

    await callback.answer(f"✅ Уровень выбран!")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
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
        logger.info("Группа успешно зарегистрирована: %s", group_data['name'])
    except Exception as e:
        logger.error(f"Ошибка при регистрации группы: {e}")

        message_source = source.message if isinstance(source, types.CallbackQuery) else source
        await message_source.answer("Произошла ошибка при регистрации группы. Попробуйте позже.")
        await state.clear()
        return

    success_msg = f"Поздравляем! Группа {group_data['name']} успешно зарегистрирована!"

    await send_band_profile(source, user_id, success_message=success_msg)
    await state.clear()

    # Отправляем Reply-клавиатуру
    kb = [
        [types.KeyboardButton(text="Моя анкета")],
        [types.KeyboardButton(text="Моя группа")],
        [types.KeyboardButton(text="Смотреть анкеты")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    message_source = source.message if isinstance(source, types.CallbackQuery) else source
    await message_source.answer("Выберите действие:", reply_markup=keyboard)