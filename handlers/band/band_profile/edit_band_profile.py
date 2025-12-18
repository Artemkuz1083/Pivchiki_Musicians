import datetime
import html
import logging
from typing import Dict, Any, List

from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.queries import get_band_data_by_user_id, update_band_year, update_band_name, update_band_genres, \
    update_band_city, update_band_description, update_band_seriousness_level
from handlers.band.band_profile.band_profile_states import BandEditingStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.enums.cities import City
from handlers.enums.genres import Genre
from handlers.enums.seriousness_level import SeriousnessLevel
from states.states_profile import ProfileStates

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.in_({"edit_band_name", "edit_band_year"}))
async def start_band_editing(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    param = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    logger.info("Пользователь %s начал редактирование параметра группы: %s", user_id, param)

    # 1. Пытаемся убрать инлайн-кнопки под профилем, чтобы пользователь не нажал их дважды
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await state.update_data(user_id=user_id)

    # 2. Определяем текст и состояние
    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params")]
    ])

    if param == "name":
        text = "🎸 <b>Введите новое название группы:</b>"
        await state.set_state(BandEditingStates.editing_band_name)
    else: # year
        text = "📅 <b>Введите новый год основания (ГГГГ):</b>"
        await state.set_state(BandEditingStates.editing_band_year)

    # 3. УДАЛЯЕМ старую Reply-клавиатуру (кнопки снизу)
    # Мы отправляем невидимое сообщение, которое тут же удаляет кнопки
    remove_msg = await callback.bot.send_message(
        chat_id=chat_id,
        text="⏳ Ожидание ввода...",
        reply_markup=ReplyKeyboardRemove()
    )
    # Сразу удаляем это сервисное сообщение, чтобы не засорять чат
    await remove_msg.delete()

    # 4. Отправляем финальное сообщение с инлайн-кнопкой "Назад"
    await callback.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=back_markup,
        parse_mode="HTML"
    )

@router.message(F.text, BandEditingStates.editing_band_name)
async def process_new_band_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s вводит новое название группы: %s", user_id, new_name)  # <-- LOG

    if len(new_name) > 100:
        logger.warning("Пользователь %s ввел слишком длинное название группы.", user_id)  # <-- LOG
        await message.answer("⚠️ Название слишком длинное (макс. 100 символов). Введите короче.")
        return

    try:
        await update_band_name(user_id, new_name)
        logger.info("Название группы пользователя %s успешно обновлено на: %s", user_id, new_name)  # <-- LOG
    except Exception as e:
        logger.error("Ошибка обновления названия группы для %s: %s", user_id, e)  # <-- LOG
        await message.answer("⚠️ Ошибка при сохранении.")
        return

    success_msg = f"✅ Название группы успешно обновлено на: <b>{html.escape(new_name)}</b>"

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_band_profile(message, user_id, success_message=success_msg)
    await state.clear()


@router.message(F.text, BandEditingStates.editing_band_year)
async def process_new_band_year(message: types.Message, state: FSMContext):
    year_text = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")

    current_year = datetime.datetime.now().year

    logger.info("Пользователь %s вводит новый год основания: %s", user_id, year_text)  # <-- LOG

    if not year_text.isdigit() or int(year_text) < 1900 or int(year_text) > current_year:
        logger.warning("Пользователь %s ввел невалидный год основания: %s", user_id, year_text)  # <-- LOG
        await message.answer(f"⚠️ Неверный формат. Введите год цифрами от 1900 до {current_year}.")
        return

    try:
        await update_band_year(user_id, year_text)
        logger.info("Год основания группы пользователя %s успешно обновлен на: %s", user_id, year_text)  # <-- LOG
    except Exception as e:
        logger.error("Ошибка обновления года группы для %s: %s", user_id, e)  # <-- LOG
        await message.answer("⚠️ Ошибка при сохранении.")
        return

    success_msg = f"✅ Год основания группы успешно обновлен на: <b>{html.escape(year_text)}</b>"

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_band_profile(message, user_id, success_message=success_msg)
    await state.clear()


@router.callback_query(F.data == "back_to_band_params",
                       BandEditingStates.editing_band_name)
async def back_from_band_name_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Редактирование названия отменено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s отменил редактирование названия группы.", user_id)  # <-- LOG

    await state.set_state(ProfileStates.select_param_to_fill)

    await send_band_profile(
        callback,
        user_id,
        success_message="❌ Редактирование отменено. Вы вернулись в меню группы."
    )
    await state.clear()


@router.callback_query(F.data == "back_to_band_params",
                       BandEditingStates.editing_band_year)
async def back_from_band_year_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Редактирование года отменено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s отменил редактирование года основания группы.", user_id)  # <-- LOG

    await state.set_state(ProfileStates.select_param_to_fill)

    await send_band_profile(
        callback,
        user_id,
        success_message="❌ Редактирование отменено. Вы вернулись в меню группы."
    )

    await state.clear()


@router.callback_query(F.data == "edit_band_genres")
async def start_editing_band_genres(callback: types.CallbackQuery, state: FSMContext):
    """Инициализирует FSMContext текущими жанрами группы и запускает выбор."""
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование жанров группы", user_id)  # <-- LOG

    await callback.answer("Загрузка жанров...")

    try:
        band_data = await get_band_data_by_user_id(user_id)
        current_genres = band_data.get("genres") if isinstance(band_data, dict) else []
    except Exception as e:
        logger.error("Ошибка при загрузке данных группы для %s: %s", user_id, e)  # <-- LOG
        await callback.message.answer("⚠️ Произошла ошибка при получении данных группы.")
        return

    standard_options = Genre.list_values()

    selected_genres = [g for g in current_genres if g in standard_options]
    own_genres = [g for g in current_genres if g not in standard_options]

    await state.update_data(user_choice_genre=selected_genres, own_user_genre=own_genres,
                            user_id=user_id)  # Добавлено user_id

    markup = make_keyboard_for_band_genre(selected_genres)

    await callback.message.edit_text(
        text="🎶 <b>Жанры</b>\n\nВыберите жанры, в которых играет ваша группа (они заменят текущие):",
        reply_markup=markup,
        parse_mode='HTML'
    )

    await state.set_state(BandEditingStates.editing_genres)


@router.callback_query(F.data.startswith("genre_"), BandEditingStates.editing_genres)
async def choose_band_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров группы."""
    user_id = callback.from_user.id
    logger.info("Пользователь %s выбрал жанр для группы: %s", user_id, callback.data)  # <-- LOG

    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        logger.info("Пользователь %s выбрал ввод собственного жанра при редактировании", user_id)  # <-- LOG
        back_button = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params")]])

        await callback.message.edit_text(
            text="📝 <b>Напишите жанр для вашей группы:</b>",
            reply_markup=back_button,
            parse_mode="HTML"
        )
        await state.set_state(BandEditingStates.inputting_own_genre)
        return

    # Логика выбора/снятия выбора
    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_band_genre(user_choice)
    )
    await state.update_data(user_choice_genre=user_choice)


@router.message(F.text, BandEditingStates.inputting_own_genre)
async def own_band_genre(message: types.Message, state: FSMContext):
    """Обработка собственного жанра для группы. Сохраняем и возвращаемся к выбору."""
    user_id = message.from_user.id
    logger.info("Пользователь %s ввел собственный жанр для группы: %s", user_id, message.text)  # <-- LOG

    new_genre = message.text.strip()
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    if new_genre.startswith('/'):
        logger.warning("Пользователь %s ввел собственный жанр, начинающийся с команды: %s", user_id,
                       new_genre)  # <-- LOG
        await message.answer("⚠️ Название жанра не может начинаться с '/'.\n<b>Напишите жанр:</b>", parse_mode="HTML")
        return

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)

    formatted_own = ", ".join([f"<i>{html.escape(g)}</i>" for g in own_user_genre])

    msg_text = (f"✅ Свой вариант добавлен: {formatted_own}\n\n"
                "<b>Выберите еще жанры, или нажмите 'Готово':</b>")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_band_genre(user_choice), parse_mode="HTML")
    await state.set_state(BandEditingStates.editing_genres)


@router.callback_query(F.data == "done_editing_band_genres")
async def done_band_genres(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки готово для жанров группы. Сохранение и возврат в профиль."""
    user_id = callback.from_user.id
    logger.info("Пользователь %s завершил выбор жанров группы", user_id)  # <-- LOG

    await callback.answer()
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])

    all_genres_user = user_choice + own_user_genre
    user_id = callback.from_user.id

    if not all_genres_user:
        logger.warning("Пользователь %s попытался сохранить пустой список жанров.", user_id)  # <-- LOG
        await callback.answer("⚠️ Пожалуйста, выберите хотя бы один жанр.", show_alert=True)
        return

    try:
        await update_band_genres(user_id, all_genres_user)
        logger.info("Жанры группы пользователя %s успешно обновлены в БД", user_id)  # <-- LOG
    except Exception as e:
        logger.error("Ошибка при сохранении жанров группы пользователя %s: %s", user_id, e)  # <-- LOG
        await state.clear()
        await send_band_profile(callback, user_id,
                                success_message="⚠️ Произошла ошибка при сохранении жанров. Попробуйте позже.")
        return

    await state.clear()
    await send_band_profile(
        callback,
        user_id,
        success_message="Жанры группы успешно обновлены!"
    )


@router.message(F.text == "🎸 Моя группа")
async def show_my_group_profile(message: types.Message):
    """
    Обрабатывает нажатие на реплай-кнопку "Моя группа" и отправляет профиль.
    """
    user_id = message.from_user.id
    await send_band_profile(
        callback_or_message=message,
        user_id=user_id,
        success_message=None
    )


def make_keyboard_for_band_genre(selected: list[str]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру жанров с выбором и кнопками 'Готово' и 'Назад'.
    Жанры расположены в две колонки.
    """
    standard_genres = Genre.list_values()

    # Формируем список всех опций для кнопок, кроме 'Готово' и 'Назад'
    genre_options_list = []
    for genre in standard_genres:
        is_selected = genre in selected and genre in standard_genres
        text = f"✅ {genre}" if is_selected else genre
        callback_data = f"genre_{genre}"
        genre_options_list.append(InlineKeyboardButton(text=text, callback_data=callback_data))

    # Добавляем "Свой вариант"
    text_custom = "Свой вариант 📝"
    callback_data_custom = "genre_Свой вариант"
    genre_options_list.append(InlineKeyboardButton(text=text_custom, callback_data=callback_data_custom))

    # Группируем кнопки жанров по две
    buttons = []
    for i in range(0, len(genre_options_list), 2):
        # Добавляем строку из двух или одной кнопки (если осталась последняя)
        buttons.append(genre_options_list[i:i + 2])

    # Добавляем кнопки "Готово" и "Назад" в отдельные строки (одна колонка)
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done_editing_band_genres")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def make_keyboard_for_city_editing(selected_city: str | None = None) -> InlineKeyboardMarkup:
    """Клавиатура городов для редактирования с кнопкой 'Назад'."""
    builder = InlineKeyboardBuilder()

    available_cities = City.list_values()

    for city in available_cities:
        text = f"✅ {city}" if city == selected_city else city
        builder.add(InlineKeyboardButton(text=text, callback_data=f"edit_city_{city}"))

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="Свой вариант 📝", callback_data="edit_city_Свой вариант"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params"))

    return builder.as_markup()


@router.callback_query(F.data == "edit_band_city")
async def start_editing_city(callback: types.CallbackQuery, state: FSMContext):
    """Начинает редактирование города."""
    user_id = callback.from_user.id
    await callback.answer("Редактирование города...")

    logger.info("Пользователь %s начал редактирование города группы", user_id)  # <-- LOG

    # Загружаем текущий город для подсветки
    try:
        band_data = await get_band_data_by_user_id(user_id)
        current_city = band_data.get("city") if isinstance(band_data.get("city"), str) else None
    except Exception as e:
        logger.error("Ошибка при загрузке данных группы для %s: %s", user_id, e)  # <-- LOG
        current_city = None

    await state.update_data(user_id=user_id, city=current_city)

    await callback.message.edit_text(
        "🏙 <b>Выберите новый город для вашей группы:</b>",
        reply_markup=make_keyboard_for_city_editing(current_city),
        parse_mode="HTML"
    )
    await state.set_state(BandEditingStates.editing_city)


@router.callback_query(F.data.startswith("edit_city_"), BandEditingStates.editing_city)
async def process_edited_city(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор города из клавиатуры при редактировании."""
    await callback.answer()
    city = callback.data.split("_")[-1]
    data = await state.get_data()
    user_id = data.get("user_id")

    if city == 'Свой вариант':
        logger.info("Пользователь %s выбрал ввод собственного города при редактировании", user_id)  # <-- LOG
        back_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад к выбору", callback_data="back_to_city_editing")]])

        await callback.message.edit_text(
            text="📝 <b>Напишите новый город для вашей группы:</b>",
            reply_markup=back_markup,
            parse_mode="HTML"
        )
        await state.set_state(BandEditingStates.inputting_own_city)
        return

    # Сохраняем и обновляем
    await update_band_city(user_id, city)
    logger.info("Город группы пользователя %s успешно обновлен на: %s", user_id, city)  # <-- LOG
    await state.clear()

    success_msg = f"✅ Город группы успешно обновлен на: <b>{html.escape(city)}</b>"
    await send_band_profile(callback, user_id, success_message=success_msg)


@router.message(F.text, BandEditingStates.inputting_own_city)
async def process_edited_own_city(message: types.Message, state: FSMContext):
    """Обрабатывает ввод собственного города при редактировании."""
    new_city = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s вводит собственный город: %s", user_id, new_city)  # <-- LOG

    if new_city.startswith('/'):
        logger.warning("Пользователь %s ввел собственный город, начинающийся с команды: %s", user_id,
                       new_city)  # <-- LOG
        await message.answer("⚠️ Название города не может начинаться с '/'. Введите корректное название.")
        return

    await update_band_city(user_id, new_city)
    logger.info("Город группы пользователя %s успешно обновлен на собственный: %s", user_id, new_city)  # <-- LOG
    await state.clear()

    success_msg = f"✅ Город группы успешно обновлен на: <b>{html.escape(new_city)}</b>"
    await send_band_profile(message, user_id, success_message=success_msg)


# Хендлер для кнопки "Назад к выбору"
@router.callback_query(F.data == "back_to_city_editing", BandEditingStates.inputting_own_city)
async def back_to_city_selection_editing(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_city = data.get("city")

    logger.info("Пользователь %s вернулся к выбору города из ввода собственного варианта",
                callback.from_user.id)  # <-- LOG

    await callback.message.edit_text(
        "🏙 <b>Выберите новый город для вашей группы:</b>",
        reply_markup=make_keyboard_for_city_editing(current_city),
        parse_mode="HTML"
    )
    await state.set_state(BandEditingStates.editing_city)
    await callback.answer()


@router.callback_query(F.data == "edit_band_description")
async def start_editing_description(callback: types.CallbackQuery, state: FSMContext):
    """Начинает редактирование описания."""
    user_id = callback.from_user.id
    await callback.answer()

    logger.info("Пользователь %s начал редактирование описания группы", user_id)  # <-- LOG

    await state.update_data(user_id=user_id)

    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params")],
        [InlineKeyboardButton(text="🗑 Удалить описание", callback_data="delete_band_description")]
    ])

    await callback.message.edit_text(
        "📝 <b>Введите новое описание группы</b> (до 1024 символов) или нажмите 'Удалить описание':",
        reply_markup=back_markup,
        parse_mode="HTML"
    )
    await state.set_state(BandEditingStates.editing_description)


@router.message(F.text, BandEditingStates.editing_description)
async def process_edited_description(message: types.Message, state: FSMContext):
    """Обрабатывает ввод нового описания."""
    new_description = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s вводит новое описание группы. Длина: %d", user_id, len(new_description))  # <-- LOG

    if len(new_description) > 1024:
        logger.warning("Пользователь %s ввел слишком длинное описание", user_id)  # <-- LOG
        await message.answer("⚠️ Описание слишком длинное. Введите короче.")
        return

    try:
        await update_band_description(user_id, new_description)
        logger.info("Описание группы пользователя %s успешно обновлено.", user_id)  # <-- LOG
    except Exception as e:
        logger.error("Ошибка сохранения описания группы для %s: %s", user_id, e)  # <-- LOG
        await message.answer("⚠️ Ошибка при сохранении.")
        return

    await state.clear()

    success_msg = f"✅ Описание группы успешно обновлено!"
    await send_band_profile(message, user_id, success_message=success_msg)


@router.callback_query(F.data == "delete_band_description", BandEditingStates.editing_description)
async def delete_band_description(callback: types.CallbackQuery, state: FSMContext):
    """Удаляет текущее описание группы."""
    await callback.answer("Описание удалено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s удалил описание группы", user_id)  # <-- LOG

    await update_band_description(user_id, None)
    await state.clear()

    success_msg = "✅ Описание группы успешно удалено!"
    await send_band_profile(callback, user_id, success_message=success_msg)


def make_keyboard_for_level_editing() -> InlineKeyboardMarkup:
    """Клавиатура уровней для редактирования с кнопкой 'Назад'."""
    builder = InlineKeyboardBuilder()

    for member in SeriousnessLevel:
        builder.add(InlineKeyboardButton(text=member.value, callback_data=f"edit_level_{member.name}"))

    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params"))
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data == "edit_band_level")
async def start_editing_level(callback: types.CallbackQuery, state: FSMContext):
    """Начинает редактирование уровня серьезности."""
    user_id = callback.from_user.id
    await callback.answer("Редактирование уровня...")

    logger.info("Пользователь %s начал редактирование уровня серьезности группы", user_id)  # <-- LOG

    await state.update_data(user_id=user_id)

    await callback.message.edit_text(
        "📊 <b>Выберите новый уровень серьезности вашей группы:</b>",
        reply_markup=make_keyboard_for_level_editing(),
        parse_mode="HTML"
    )
    await state.set_state(BandEditingStates.editing_seriousness_level)


@router.callback_query(F.data.startswith("edit_level_"), BandEditingStates.editing_seriousness_level)
async def process_edited_level(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор нового уровня серьезности."""
    level_key = callback.data.split("_")[-1]
    data = await state.get_data()
    user_id = data.get("user_id")

    logger.info("Пользователь %s выбрал новый уровень серьезности: %s", user_id, level_key)  # <-- LOG

    try:
        selected_level = SeriousnessLevel[level_key]
    except KeyError:
        logger.error("Пользователь %s выбрал неверный уровень серьезности: %s", user_id, level_key)  # <-- LOG
        await callback.answer("⚠️ Неверный выбор уровня.")
        return

    await update_band_seriousness_level(user_id, selected_level.value)
    logger.info("Уровень серьезности группы пользователя %s успешно обновлен на: %s", user_id,
                selected_level.value)  # <-- LOG
    await state.clear()

    success_msg = f"✅ Уровень серьезности успешно обновлен на: <b>{html.escape(selected_level.value)}</b>"
    await send_band_profile(callback, user_id, success_message=success_msg)


@router.callback_query(F.data == "back_to_band_params")
async def universal_back_to_band_profile(callback: types.CallbackQuery, state: FSMContext):
    """
    Исправленный универсальный хендлер.
    Убрали BandEditingStates из аргументов, чтобы не было ошибки TypeError.
    """
    user_id = callback.from_user.id

    # Мы можем логгировать текущее состояние перед очисткой
    current_state = await state.get_state()
    logger.info("Пользователь %s отменил редактирование (был в %s) и возвращается в профиль группы.", user_id,
                current_state)

    await callback.answer("Редактирование отменено.")

    # Сбрасываем стейт полностью
    await state.clear()

    # Отправляем анкету группы
    await send_band_profile(
        callback,
        user_id,
        success_message="❌ Изменения не сохранены. Вы вернулись в меню группы."
    )