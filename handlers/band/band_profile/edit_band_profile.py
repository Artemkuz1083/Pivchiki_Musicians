import datetime
from typing import Dict, Any, List

from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.queries import get_band_data_by_user_id, update_band_year, update_band_name, update_band_genres
from handlers.band.band_profile.band_profile_states import BandEditingStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.enums.genres import Genre
from handlers.registration.registration import logger
from states.states_profile import ProfileStates

router = Router()


@router.callback_query(F.data.in_({"edit_band_name", "edit_band_year"}))
async def start_band_editing(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    param = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    await state.update_data(user_id=user_id)

    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_band_params")]
    ])

    if param == "name":
        await callback.message.edit_text(
            "Введите новое название группы:",
            reply_markup=back_markup
        )
        await state.set_state(BandEditingStates.editing_band_name)
    elif param == "year":
        await callback.message.edit_text(
            "Введите новый год основания (ГГГГ):",
            reply_markup=back_markup
        )
        await state.set_state(BandEditingStates.editing_band_year)


@router.message(F.text, BandEditingStates.editing_band_name)
async def process_new_band_name(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    user_id = data.get("user_id")

    if len(new_name) > 100:
        await message.answer("Название слишком длинное. Введите короче.")
        return

    await update_band_name(user_id, new_name)

    success_msg = f"✅ Имя группы успешно обновлено на: **{new_name}**"

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_band_profile(message, user_id, success_message=success_msg)
    await state.clear()


@router.message(F.text, BandEditingStates.editing_band_year)
async def process_new_band_year(message: types.Message, state: FSMContext):
    year_text = message.text
    data = await state.get_data()
    user_id = data.get("user_id")

    current_year = datetime.datetime.now().year

    if not year_text.isdigit() or int(year_text) < 1900 or int(year_text) > current_year:
        await message.answer(f"Неверный формат. Введите год цифрами от 1900 до {current_year}.")
        return

    await update_band_year(user_id, year_text)

    success_msg = f"✅ Год основания группы успешно обновлен на: **{year_text}**"

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_band_profile(message, user_id, success_message=success_msg)
    await state.clear()


@router.callback_query(F.data == "back_to_band_params",
                       BandEditingStates.editing_band_name)
async def back_from_band_name_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Редактирование названия отменено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    await state.set_state(ProfileStates.select_param_to_fill)

    await send_band_profile(
        callback,
        user_id,
        success_message="Редактирование отменено. Вы вернулись в меню группы."
    )
    await state.clear()


@router.callback_query(F.data == "back_to_band_params",
                       BandEditingStates.editing_band_year)
async def back_from_band_year_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Редактирование года отменено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    await state.set_state(ProfileStates.select_param_to_fill)

    await send_band_profile(
        callback,
        user_id,
        success_message="Редактирование отменено. Вы вернулись в меню бэнда."
    )

    await state.clear()

@router.callback_query(F.data == "edit_band_genres")
async def start_editing_band_genres(callback: types.CallbackQuery, state: FSMContext):
    """Инициализирует FSMContext текущими жанрами группы и запускает выбор."""
    logger.info("Пользователь %s начал редактирование жанров группы", callback.from_user.id)

    user_id = callback.from_user.id
    await callback.answer("Запуск редактирования жанров...")

    try:
        band_data = await get_band_data_by_user_id(user_id)
        current_genres = band_data.get("genres") if isinstance(band_data, dict) else []
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных группы: {e}")
        await callback.message.answer("Произошла ошибка при получении данных группы.")
        return

    standard_options = Genre.list_values()

    selected_genres = [g for g in current_genres if g in standard_options]
    own_genres = [g for g in current_genres if g not in standard_options]

    await state.update_data(user_choice_genre=selected_genres, own_user_genre=own_genres)

    markup = make_keyboard_for_band_genre(selected_genres)

    await callback.message.edit_text(
        text="Выберите жанры, в которых играет ваша группа (они заменят текущие):",
        reply_markup=markup,
        parse_mode='Markdown'
    )

    await state.set_state(BandEditingStates.editing_genres)

@router.callback_query(F.data.startswith("genre_"), BandEditingStates.editing_genres)
async def choose_band_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров группы."""
    logger.info("Пользователь %s выбрал жанр для группы: %s", callback.from_user.id, callback.data)

    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        back_button = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="edit_band_genres")]])

        await callback.message.edit_text(
            text="Напишите жанр для вашей группы:",
            reply_markup=back_button
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
    logger.info("Пользователь %s ввел собственный жанр для группы: %s", message.from_user.id, message.text)

    new_genre = message.text
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)

    msg_text = (f"Свой вариант: {', '.join(own_user_genre)}\n"
                "Отлично! Теперь выберите жанры, в которых играет ваша группа:")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_band_genre(user_choice))
    await state.set_state(BandEditingStates.editing_genres)

@router.callback_query(F.data == "done_editing_band_genres")
async def done_band_genres(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки готово для жанров группы. Сохранение и возврат в профиль."""
    logger.info("Пользователь %s завершил выбор жанров группы", callback.from_user.id)

    await callback.answer()
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])

    all_genres_user = user_choice + own_user_genre
    user_id = callback.from_user.id

    if not all_genres_user:
        await callback.answer("Пожалуйста, выберите хотя бы один жанр.")
        return

    try:
        await update_band_genres(user_id, all_genres_user)
        logger.info("Жанры группы пользователя %s успешно обновлены в БД", user_id)
    except Exception as e:
        logger.error("Ошибка при сохранении жанров группы пользователя %s: %s", user_id, e)
        await state.clear()
        await send_band_profile(callback, user_id,
                                success_message="Произошла ошибка при сохранении жанров. Попробуйте позже.")
        return

    await state.clear()
    await send_band_profile(
        callback,
        user_id,
        success_message="Жанры группы успешно обновлены!"
    )

@router.message(F.text == "Моя группа")
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
    standard_genres = Genre.list_values()

    all_genre_options = [g for g in standard_genres]
    if "Свой вариант" not in all_genre_options:
        all_genre_options.append("Свой вариант")

    buttons = []

    for genre in all_genre_options:
        is_selected = genre in selected and genre in standard_genres

        if genre == "Свой вариант":
            text = "Свой вариант 📝"
        else:
            text = f"✅ {genre}" if is_selected else genre
        callback_data = f"genre_{genre}"

        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done_editing_band_genres")])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_params")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)