from aiogram import F, types, Router, Bot, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.band.band_registration.band_registration_states import BandRegistrationStates
from handlers.band.showing_band_profile_logic import send_band_profile
from handlers.profile.profile_keyboards import make_keyboard_for_genre
from handlers.registration.registration import logger

router = Router()

@router.message(F.text == "Зарегистрировать группу")
async def start_group_registration(message: types.Message, state: FSMContext):
    """Начало регистрации группы: запрашивает название."""

    await message.answer(
        "**Начнем регистрацию группы**\n\n"
        "Напишите название вашей группы",
        parse_mode='Markdown'
    )

    await state.update_data(user_id=message.from_user.id)
    await state.set_state(BandRegistrationStates.filling_name)


import datetime




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
# ... (остальные импорты)

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
async def done_group_registration(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки готово для жанров группы и сохранение всех данных."""
    await callback.answer()
    data = await state.get_data()

    #Сборка данных
    all_genres_user = data.get("user_choice_genre", []) + data.get("own_user_genre", [])

    if not all_genres_user:
        await callback.answer("Пожалуйста, выберите жанры.")
        return

    #Подготовка данных для сохранения
    group_data = {
        "user_id": data.get("user_id"),
        "name": data.get("group_name"),
        "foundation_date": data.get("foundation_date"),
        "genres": all_genres_user
    }

    #Сохранение в БД
    try:
        # Вам нужно будет создать эту функцию, которая сохранит group_data в таблицу Group
        await create_group(group_data)
    except Exception as e:
        logger.error(f"Ошибка при регистрации группы: {e}")
        await callback.message.edit_text("Произошла ошибка при регистрации группы. Попробуйте позже.")
        await state.clear()
        return

    success_msg = f"Поздравляем! Группа {group_data['name']} успешно зарегистрирована!"

    await send_band_profile(
        callback,
        group_data,
        success_message=success_msg
    )

    # Очистка FSM
    await state.clear()
    await state.clear()