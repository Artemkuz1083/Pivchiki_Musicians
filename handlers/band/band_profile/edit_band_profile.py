import datetime

from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from handlers.band.band_profile.band_profile_states import BandEditingStates
from handlers.band.band_registration.band_registration_states import BandRegistrationStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.profile import genres
from handlers.profile.genres import Genre
from handlers.profile.profile_keyboards import make_keyboard_for_genre
from handlers.registration.registration import logger
from states.states_profile import ProfileStates

router = Router()

@router.callback_query(F.data.startswith("edit_band_"))
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
            "Введите новое название бэнда:",
            reply_markup=back_markup
        )
        await state.set_state(BandEditingStates.editing_band_name)
    elif param == "year":
        await callback.message.edit_text(
            "Введите новый год основания (ГГГГ):",
            reply_markup=back_markup
        )
        await state.set_state(BandEditingStates.editing_band_year)
    elif param == "genres":
        # Переход к логике жанров
        await callback.message.answer("Запуск редактирования жанров...")
    else:
        await callback.message.answer("Неизвестный параметр редактирования.")


@router.message(F.text, BandEditingStates.editing_band_name)
async def process_new_band_name(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    user_id = data.get("user_id")

    if len(new_name) > 100:
        await message.answer("Название слишком длинное. Введите короче.")
        return

    # 1. Обновление БД (Предполагается, что существует)
    await update_band_name(user_id, new_name)

    # 2. Возврат профиля
    success_msg = f"✅ Имя бэнда успешно обновлено на: **{new_name}**"
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

    # 1. Обновление БД (Предполагается, что существует)
    await update_band_year(user_id, year_text)

    # 2. Возврат профиля
    success_msg = f"✅ Год основания бэнда успешно обновлен на: **{year_text}**"
    await state.set_state(ProfileStates.select_param_to_fill)

    await send_band_profile(message, user_id, success_message=success_msg)
    await state.clear()


@router.callback_query(F.data == "back_to_band_params",
                       BandEditingStates.editing_band_name | BandEditingStates.editing_band_year)
async def back_from_band_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Редактирование отменено.")
    data = await state.get_data()
    user_id = data.get("user_id")

    # 1. Сброс состояния
    await state.set_state(ProfileStates.select_param_to_fill)

    # 2. Возврат профиля группы
    await send_band_profile(
        callback,
        user_id,
        success_message="Редактирование отменено. Вы вернулись в меню группы."
    )
    await state.clear()


# 3. Хендлер, который ловит нажатие "Жанры" для Бэнда
@router.callback_query(F.data == "edit_band_genres")
async def start_editing_band_genres(callback: types.CallbackQuery, state: FSMContext):
    """Инициализирует FSMContext текущими жанрами Бэнда и запускает выбор."""

    user_id = callback.from_user.id
    await callback.answer("Запуск редактирования жанров...")

    #Загружаем текущие данные группы (Предполагается, что get_band_data_by_user_id существует)
    band_data = await get_band_data_by_user_id(user_id)
    current_genres = band_data.get("genres", [])

    # 2. Разделяем жанры на стандартные и собственные
    standard_options = Genre.list_values()

    selected_genres = [g for g in current_genres if g in standard_options]
    own_genres = [g for g in current_genres if g not in standard_options]

    # 3. Инициализируем FSMContext
    await state.update_data(user_choice_genre=selected_genres)
    await state.update_data(own_user_genre=own_genres)

    # 4. Отправляем клавиатуру и переводим состояние
    markup = make_keyboard_for_genre(selected_genres)

    await callback.message.edit_text(
        text="**Выберите жанры**, в которых играет ваш бэнд (они заменят текущие):",
        reply_markup=markup,
        parse_mode='Markdown'
    )

    # Используем состояние для выбора жанров, определенное ранее для группы
    await state.set_state(BandRegistrationStates.selecting_genres)


@router.callback_query(F.data == "done_genres", BandRegistrationStates.selecting_genres)
async def done_band_genre_editing(callback: types.CallbackQuery, state: FSMContext):
    """Сохраняет обновленные жанры Бэнда и возвращает в меню профиля."""
    await callback.answer()
    data = await state.get_data()

    user_choice = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])
    all_genres_band = user_choice + own_user_genre  # Объединяем, это список строк
    user_id = callback.from_user.id

    if not all_genres_band:
        await callback.answer("Пожалуйста, выберите хотя бы один жанр.")
        return

    # 1. Сохранение в БД
    try:
        # update_band_genres принимает список строк, что соответствует нашим данным
        await update_band_genres(user_id, all_genres_band)
    except Exception as e:
        logger.error(f"Ошибка при обновлении жанров Бэнда для {user_id}: {e}")
        await callback.message.answer("❌ Произошла ошибка при сохранении жанров. Попробуйте позже.")
        await state.clear()
        return

    # 2. Успех: устанавливаем основное состояние и отправляем анкету
    await state.set_state(ProfileStates.select_param_to_fill)

    success_msg = f"✅ Жанры бэнда успешно обновлены!"

    await send_band_profile(
        callback,
        user_id,
        success_message=success_msg
    )

    await state.clear()