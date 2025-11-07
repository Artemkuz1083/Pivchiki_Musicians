import asyncio
from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.enums import PerformanceExperience
from database.queries import update_user, update_instrument_level, update_user_experience, update_user_theory_level, \
    save_user_profile_photo, save_user_audio, get_user
from states.states_profile import ProfileStates

router = Router()


def get_profile_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="Дозаполнить профиль"),
        KeyboardButton(text="Редактировать профиль"),
    )

    builder.row(
        KeyboardButton(text="Назад")
    )

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_instrument_selection_keyboard(instruments: list) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру со списком инструментов пользователя."""
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (ур. {instrument.proficiency_level})",
            callback_data=f"select_inst:{instrument.id}"
        ))

    builder.row(InlineKeyboardButton(text="Назад", callback_data="back_to_params"))
    return builder.as_markup()


def get_experience_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру с вариантами опыта выступлений."""
    builder = InlineKeyboardBuilder()

    # Итерируемся по вашему Enum
    for exp_type in PerformanceExperience:
        builder.row(InlineKeyboardButton(
            text=exp_type.value,
            callback_data=f"select_exp:{exp_type.name}"
        ))

    builder.row(InlineKeyboardButton(text="Отмена", callback_data="back_to_params"))

    return builder.as_markup()

def get_profile_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора параметров профиля."""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Возраст", callback_data="edit_age"))
    builder.row(InlineKeyboardButton(text="Уровень владения", callback_data="edit_level"))
    builder.row(InlineKeyboardButton(text="Опыт выступлений", callback_data="edit_experience"))
    builder.row(InlineKeyboardButton(text="Уровень теории", callback_data="edit_theory"))
    builder.row(InlineKeyboardButton(text="Демонстрационные файлы", callback_data="edit_files"))
    builder.row(InlineKeyboardButton(text="Фото", callback_data="edit_photo"))

    return builder.as_markup()


def get_theory_level_keyboard_verbal() -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру с вербальными градациями уровня теории."""
    builder = InlineKeyboardBuilder()
    GRADATIONS = {
        "Совсем не знаю (0)": 0,
        "Базовые знания (1)": 1,
        "Учусь (2)": 2,
        "Средний уровень (3)": 3,
        "Продвинутый (4)": 4,
        "Эксперт (5)": 5,
    }

    # Создаем кнопки
    for text, level in GRADATIONS.items():
        # callback_data: 'set_theory_level:0', 'set_theory_level:1' и т.д.
        builder.button(
            text=text,
            callback_data=f"set_theory_level:{level}"
        )

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="Отмена", callback_data="back_to_params"))
    return builder.as_markup()

def rating_to_stars(level: int) -> str:
    level = max(0, level)
    return "⭐️" * level


@router.callback_query(F.data == "my_profile")
async def show_profile_from_callback(callback: types.CallbackQuery):
    """
    Этот хендлер ловит нажатие ИНЛАЙН-КНОПКИ "Моя анкета"
    """
    await callback.answer()
    user_id = callback.from_user.id

    try:
        user_obj = await get_user(user_id)
    except Exception as e:
        print(f"Ошибка при получении данных пользователя: {e}")
        await callback.message.answer("Произошла ошибка при доступе к вашему профилю. Пожалуйста, попробуйте позже.")
        return

    if user_obj:
        stars_knowledge = rating_to_stars(user_obj.theoretical_knowledge_level)

        experience_display = getattr(user_obj.has_performance_experience, 'value',
                                     str(user_obj.has_performance_experience))

        genres_list = user_obj.genres or ["Не указано"]
        genres_display = ", ".join(genres_list)

        if user_obj.instruments:
            instruments_lines = []
            for instrument in user_obj.instruments:
                stars_proficiency = rating_to_stars(instrument.proficiency_level)
                instruments_lines.append(
                    f"  • **{instrument.name}:** {stars_proficiency}"
                )
            instruments_display = "\n".join(instruments_lines)
        else:
            instruments_display = "Не указаны"

        photo_display = "Загружено" if user_obj.photo_path else "Не загружено"

        audio_display = "Загружено" if user_obj.audio_path else "Не загружено"

        external_link_display = user_obj.external_link if user_obj.external_link else "Не указана"

        profile_text = (
            f"**Ваша анкета**\n\n"
            f"**Имя:** {user_obj.name or 'Не указано'}\n"
            f"**Возраст:** {user_obj.age or 'Не указан'}\n"
            f"**Город:** {user_obj.city or 'Не указан'}\n\n"

            f"**Уровень теоретических знаний:** {stars_knowledge}\n"
            f"**Опыт выступлений:** {experience_display}\n\n"

            f"**Фото профиля:** {photo_display}\n"
            f"**Демо-трек (Аудио/ГС):** {audio_display}\n"
            f"**Внешняя ссылка:** {external_link_display}\n\n"  

            f"**Любимые жанры:** {genres_display}\n\n"

            f"**Инструменты:**\n"
            f"{instruments_display}\n\n"

            "Спасибо, что пользуетесь нашим сервисом!"
        )

        keyboard = None
        await callback.message.answer(
            profile_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    else:
        reply_keyboard_builder = ReplyKeyboardBuilder()
        reply_keyboard_builder.row(
            KeyboardButton(text="Создать анкету")
        )

        await callback.message.answer(
            "Ваша анкета не найдена. Создайте ее сейчас:",
            reply_markup=reply_keyboard_builder.as_markup(resize_keyboard=True)
        )


@router.callback_query(F.data == "fill_profile")
async def start_filling_profile(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    # Устанавливаем состояние выбора параметра
    await state.set_state(ProfileStates.select_param_to_fill)

    # Отправляем клавиатуру
    await callback.message.edit_text(
        "Выберите параметр, который вы хотите установить:",
        reply_markup=get_profile_selection_keyboard()
    )


@router.callback_query(F.data == "edit_age", ProfileStates.select_param_to_fill)
async def ask_for_age(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Возраст' и запрашивает новый возраст."""
    await callback.answer()
    await state.set_state(ProfileStates.filling_age)

    await callback.message.edit_text(
        "**Введите ваш новый возраст.**\n\n"
        "Возраст должен быть целым числом (от 0 до 100).",
        parse_mode='Markdown'
    )


@router.message(ProfileStates.filling_age, F.text)
async def process_new_age(message: types.Message, state: FSMContext):
    """Обрабатывает введенный пользователем возраст, сохраняет его и возвращает к выбору параметров."""
    user_id = message.from_user.id
    new_age_str = message.text.strip()
    try:
        new_age = int(new_age_str)
        if not (0 <= new_age <= 100):
            raise ValueError("Возраст вне диапазона")
    except ValueError:
        await message.answer(
            "**Неверный ввод.** Пожалуйста, введите возраст как целое число от 0 до 100"
        )
        return

    try:
        await update_user(user_id=user_id, age=new_age)

    except Exception as e:
        print(f"Ошибка сохранения возраста в БД: {e}")
        await message.answer("Произошла ошибка при сохранении возраста. Пожалуйста, попробуйте позже.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    await message.answer(
        f"**Возраст успешно обновлен!**\n\n"
        f"Ваш новый возраст: **{new_age}**.\n\n"
        f"Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "edit_level", ProfileStates.select_param_to_fill)
async def start_editing_level(callback: types.CallbackQuery, state: FSMContext):
    """
    Срабатывает при нажатии на 'Уровень владения', получает список инструментов
    и предлагает пользователю выбрать, какой инструмент редактировать.
    """
    await callback.answer()
    user_id = callback.from_user.id
    user_obj = await get_user(user_id)

    if not user_obj or not user_obj.instruments:
        await callback.message.edit_text(
            "У вас пока нет добавленных инструментов. Сначала добавьте их!",
            reply_markup=get_profile_selection_keyboard()
        )
        return

    instrument_keyboard = get_instrument_selection_keyboard(user_obj.instruments)

    await state.set_state(ProfileStates.select_instrument_to_edit)

    await callback.message.edit_text(
        "**Выберите инструмент**, уровень владения которым вы хотите изменить:",
        reply_markup=instrument_keyboard,
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("select_inst:"), ProfileStates.select_instrument_to_edit)
async def ask_for_new_level(callback: types.CallbackQuery, state: FSMContext):
    """Сохраняет ID инструмента, устанавливает состояние ожидания уровня и запрашивает ввод."""
    await callback.answer()
    instrument_id = int(callback.data.split(":")[1])
    await state.update_data(current_instrument_id=instrument_id)
    await state.set_state(ProfileStates.filling_level)

    await callback.message.edit_text(
        "**Введите новый уровень владения** (от 1 до 5):\n\n"
        "1 - новичок, 5 - мастер.",
        parse_mode='Markdown'
    )


@router.message(ProfileStates.filling_level, F.text)
async def process_new_level(message: types.Message, state: FSMContext):
    """Обрабатывает введенный уровень владения, сохраняет его и возвращает к выбору параметров."""
    user_id = message.from_user.id
    new_level_str = message.text.strip()
    data = await state.get_data()
    instrument_id = data.get("current_instrument_id")

    try:
        new_level = int(new_level_str)
        if not (1 <= new_level <= 5):
            raise ValueError("Уровень вне диапазона")
    except ValueError:
        await message.answer(
            "**Неверный ввод.** Пожалуйста, введите уровень как целое число от 1 до 5."
        )
        return

    try:
        await update_instrument_level(instrument_id=instrument_id, new_level=new_level)

    except Exception as e:
        print(f"Ошибка сохранения уровня в БД: {e}")
        await message.answer("Произошла ошибка при сохранении уровня. Пожалуйста, попробуйте позже.")

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()

    await message.answer(
        f"**Уровень владения успешно обновлен!**\n\n"
        f"Ваш новый уровень: {rating_to_stars(new_level)}.\n\n"
        f"Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "edit_experience", ProfileStates.select_param_to_fill)
async def start_editing_experience(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Опыт выступлений' и предлагает выбрать вариант из Enum."""
    await callback.answer()
    await state.set_state(ProfileStates.selecting_experience_type)
    await callback.message.edit_text(
        "**Выберите ваш текущий опыт выступлений:**",
        reply_markup=get_experience_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("select_exp:"), ProfileStates.selecting_experience_type)
async def process_experience_type(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор типа опыта, сохраняет его в БД и возвращает в главное меню.
    """
    await callback.answer()
    user_id = callback.from_user.id
    experience_name = callback.data.split(":")[1]

    try:
        selected_experience = PerformanceExperience(experience_name)
    except KeyError:
        await callback.message.edit_text("Ошибка выбора. Попробуйте снова.")
        return
    await update_user_experience(user_id, selected_experience)
    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()
    await callback.message.edit_text(
        f"**Опыт выступлений обновлен:** {selected_experience.value}.\n\n"
        f"Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "edit_theory", ProfileStates.select_param_to_fill)
async def start_selecting_theory_level(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Уровень теории' и показывает клавиатуру с вербальными градациями."""
    await callback.answer()
    await state.set_state(ProfileStates.selecting_theory_level)
    await callback.message.edit_text(
        "**🎶 Выберите ваш уровень теоретических знаний:**",
        reply_markup=get_theory_level_keyboard_verbal(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("set_theory_level:"), ProfileStates.selecting_theory_level)
async def process_selected_theory_level(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбранный уровень теории, сохраняет его в БД и возвращает к выбору параметров."""
    await callback.answer()
    user_id = callback.from_user.id
    try:
        new_level = int(callback.data.split(":")[1])
    except ValueError:
        await callback.message.edit_text("Ошибка выбора. Попробуйте снова.")
        return
    try:
        await update_user_theory_level(user_id=user_id, theory_level=new_level)

    except Exception as e:
        print(f"Ошибка сохранения уровня теории в БД: {e}")
        await callback.message.edit_text("Произошла ошибка при сохранении уровня. Пожалуйста, попробуйте позже.")

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()
    await callback.message.edit_text(
        f"**Уровень теории успешно обновлен!**\n\n"
        f"Ваш новый уровень теории: **{new_level}**.\n\n"
        f"Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "edit_files", ProfileStates.select_param_to_fill)
async def start_uploading_files(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Загрузка файлов' и переводит в режим ожидания ОДНОГО аудио/ГС."""
    await callback.answer()
    await state.set_data({})
    await state.set_state(ProfileStates.uploading_files)
    await callback.message.edit_text(
        "**Пришлите аудиофайл или запишите голосовое сообщение**, чтобы продемонстрировать ваш уровень. \n\n"
        "Ваш файл заменит текущий демо-трек.",
        parse_mode='Markdown'
    )


@router.message(ProfileStates.uploading_files, F.audio | F.voice)
async def handle_uploaded_audio_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_id = None

    if message.audio:
        file_id = message.audio.file_id
        content_type = "аудиофайл"

    elif message.voice:
        file_id = message.voice.file_id
        content_type = "голосовое сообщение"

    if file_id:
        try:
            await save_user_audio(user_id=user_id, file_id=file_id)
        except Exception as e:
            print(f"Ошибка сохранения аудио в БД: {e}")
            await message.answer("Произошла ошибка при сохранении файла. Пожалуйста, попробуйте позже.")
            return

        await state.set_state(ProfileStates.select_param_to_fill)
        await state.clear()

        await message.answer(
            f"**Демонстрационный {content_type} обновлен!**\n\n"
            f"Выберите следующий параметр для изменения:",
            reply_markup=get_profile_selection_keyboard(),
            parse_mode='Markdown'
        )


@router.callback_query(F.data == "edit_link", ProfileStates.select_param_to_fill)
async def start_filling_link(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Ссылка' и переводит в режим ожидания URL."""
    await callback.answer()
    await state.set_state(ProfileStates.filling_external_link)
    await callback.message.edit_text(
        "**Пришлите ссылку на ваш плеер** (например, ЯндексМузыка, VK Музыка, YouTube и т.д.).\n\n"
        "Эта ссылка заменит текущую.",
        parse_mode='Markdown'
    )

@router.callback_query(F.data == "edit_photo", ProfileStates.select_param_to_fill)
async def start_uploading_photo(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Фото' и переводит в режим ожидания ОДНОЙ фотографии."""
    await callback.answer()
    await state.set_state(ProfileStates.uploading_profile_photo)
    await callback.message.edit_text(
        "**Загрузите фотографию для вашего профиля.**\n\n",
        parse_mode='Markdown'
    )


@router.message(ProfileStates.uploading_profile_photo, F.photo)
async def handle_uploaded_photo(message: types.Message, state: FSMContext):
    """
    Обрабатывает загруженное фото, сохраняет его file_id в photo_path
    и возвращает пользователя в меню.
    """
    user_id = message.from_user.id
    photo_file_id = message.photo[-1].file_id
    try:
        await save_user_profile_photo(user_id=user_id, file_id=photo_file_id)

    except Exception as e:
        print(f"Ошибка сохранения фото в БД: {e}")
        await message.answer("Произошла ошибка при сохранении фото. Пожалуйста, попробуйте позже.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()

    await message.answer(
        f"**Фотография профиля успешно обновлена!**\n\n"
        f"Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )

# Хендлер, который будет реагировать на нажатие кнопки "Редактировать профиль"
@router.callback_query(F.data == "edit_profile")
async def process_edit_profile(callback: types.CallbackQuery):
    await callback.answer()

    # Здесь начнется ваша логика редактирования профиля
    await callback.message.edit_text("Вы начали процесс редактирования профиля...")

@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.answer()
