import asyncio
from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.enums import PerformanceExperience
from database.queries import update_user, update_instrument_level, update_user_experience, update_user_theory_level, \
    save_user_profile_photo, save_user_audio, get_user, update_user_city, update_user_name, update_user_genres
from handlers.registration.registration import make_keyboard_for_instruments, logger
from states.states_profile import ProfileStates
from states.states_registration import RegistrationStates

router = Router()


async def send_updated_profile(message: types.Message | types.CallbackQuery, user_id: int,
                               success_message: str | None = None):
    """
    Загружает свежие данные пользователя, форматирует анкету,
    отправляет медиафайлы и затем отправляет текстовое сообщение с клавиатурой.
    """
    bot = message.bot
    # Определяем Chat ID
    chat_id = message.chat.id if isinstance(message, types.Message) else message.message.chat.id

    # 1. Скрытие/Удаление старого сообщения (только для CallbackQuery)
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        try:
            # Пытаемся удалить или отредактировать старое сообщение, чтобы избежать дублирования
            await message.message.delete()
        except Exception:
            pass

    try:
        user_obj = await get_user(user_id)
    except Exception as e:
        print(f"Ошибка при получении данных пользователя в send_updated_profile: {e}")
        await bot.send_message(chat_id, "Произошла ошибка при доступе к профилю.")
        return

    if not user_obj:
        await bot.send_message(chat_id, "Ваша анкета не найдена.")
        return

    knowledge_level = user_obj.theoretical_knowledge_level if user_obj.theoretical_knowledge_level is not None else 0
    stars_knowledge = rating_to_stars(knowledge_level)

    experience_display = getattr(user_obj.has_performance_experience, 'value',
                                 str(user_obj.has_performance_experience) or 'Не указано')

    genres_list = user_obj.genres or ["Не указано"]
    genres_display = ", ".join(genres_list)

    instruments_lines = []
    if user_obj.instruments:
        for instrument in user_obj.instruments:
            proficiency_level = instrument.proficiency_level if instrument.proficiency_level is not None else 0
            stars_proficiency = rating_to_stars(proficiency_level)
            instruments_lines.append(
                f"  • **{instrument.name}:** {stars_proficiency}"
            )
        instruments_display = "\n".join(instruments_lines)
    else:
        instruments_display = "Не указаны"

    external_link_display = user_obj.external_link if user_obj.external_link else "Не указана"

    profile_text = (
        f"{success_message}\n\n" if success_message else ""
        f"**Ваша обновленная анкета**\n\n"
        f"**Имя:** {user_obj.name or 'Не указано'}\n"
        f"**Возраст:** {user_obj.age or 'Не указано'}\n"
        f"**Город:** {user_obj.city or 'Не указано'}\n\n"

        f"**Уровень теоретических знаний:** {stars_knowledge}\n"
        f"**Опыт выступлений:** {experience_display}\n\n"

        f"**Внешняя ссылка:** {external_link_display}\n\n"

        f"**Любимые жанры:** {genres_display}\n\n"

        f"**Инструменты:**\n"
        f"{instruments_display}\n\n"

        "Выберите следующий параметр для изменения или нажмите 'Назад':"

    )

    if user_obj.photo_path:
        try:
            # Отправляем фото по file_id
            await bot.send_photo(chat_id, photo=user_obj.photo_path, caption="Фото профиля:")
        except Exception as e:
            # Если file_id устарел или неверен, отправляем уведомление
            print(f"Ошибка отправки фото по file_id: {e}")
            await bot.send_message(chat_id, "Фото профиля не удалось загрузить.")

    # Отправка Аудио
    if user_obj.audio_path:
        try:
            await bot.send_audio(chat_id, audio=user_obj.audio_path, caption="Демо-трек:")
        except Exception as e:
            print(f"Ошибка отправки аудио по file_id: {e}")
            await bot.send_message(chat_id, "Демо-трек не удалось загрузить.")

    keyboard = get_profile_selection_keyboard()

    # Отправляем новое текстовое сообщение
    await bot.send_message(
        chat_id,
        profile_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


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

    # Итерируемся по Enum
    for exp_type in PerformanceExperience:
        builder.row(InlineKeyboardButton(
            text=exp_type.value,
            callback_data=f"select_exp:{exp_type.name}"
        ))

    builder.row(InlineKeyboardButton(text="Назад", callback_data="back_to_params"))

    return builder.as_markup()


def get_profile_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора параметров профиля."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Имя", callback_data="edit_name"))
    builder.row(InlineKeyboardButton(text="Город", callback_data="edit_city"))
    builder.row(InlineKeyboardButton(text="Жанры", callback_data="edit_genres"))
    builder.row(InlineKeyboardButton(text="Инструменты", callback_data="edit_instruments"))
    builder.row(InlineKeyboardButton(text="Возраст", callback_data="edit_age"))
    builder.row(InlineKeyboardButton(text="Уровень владения", callback_data="edit_level"))
    builder.row(InlineKeyboardButton(text="Опыт выступлений", callback_data="edit_experience"))
    builder.row(InlineKeyboardButton(text="Уровень теории", callback_data="edit_theory"))
    builder.row(InlineKeyboardButton(text="Демонстрационные файлы", callback_data="edit_files"))
    builder.row(InlineKeyboardButton(text="Внешняя ссылка", callback_data="edit_link"))
    builder.row(InlineKeyboardButton(text="Фото", callback_data="edit_photo"))
    #builder.row(InlineKeyboardButton(text="Назад", callback_data="back_from_profile"))
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

def get_level_rating_keyboard_verbal(instrument_id: int) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру с вербальными градациями для уровня владения инструментом (1-5)."""
    builder = InlineKeyboardBuilder()

    # обозначения для уровней 1-5
    # Ключ: Текстовое отображение | Значение: Уровень (1-5)
    GRADATIONS = {
        "Новичок (Только начал)": 1,
        "Ученик (Осваиваю базу)": 2,
        "Любитель (Играю уверенно)": 3,
        "Продвинутый (Могу импровизировать)": 4,
        "Мастер (Профессиональный уровень)": 5,
    }

    # Создаем кнопки
    for text, level in GRADATIONS.items():
        # Callback-данные содержат: "set_level:{instrument_id}:{level}"
        callback_data = f"set_level:{instrument_id}:{level}"
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))

    # Кнопка "Назад"
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back_to_params"))

    return builder.as_markup()

def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level


async def _show_profile_logic(event: types.Message | types.CallbackQuery, state: FSMContext):
    """
    Универсальная логика для показа анкеты, вызываемая как по тексту, так и по колбэку.
    """
    user_id = event.from_user.id

    # 1. Если это CallbackQuery, нужно ответить на него.
    if isinstance(event, types.CallbackQuery):
        await event.answer()
        # Для удобства, используем message_source для отправки ответов
        message_source = event.message
    else:
        message_source = event

    try:
        user_obj = await get_user(user_id)
    except Exception as e:
        print(f"Ошибка при получении данных пользователя: {e}")
        await message_source.answer("Произошла ошибка при доступе к вашему профилю. Пожалуйста, попробуйте позже.")
        return

    # 2. Устанавливаем состояние для редактирования
    await state.set_state(ProfileStates.select_param_to_fill)

    if user_obj:
        # Используем универсальную функцию отправки, которая знает, как обработать Message или CallbackQuery
        await send_updated_profile(event, user_id)

    else:
        reply_keyboard_builder = ReplyKeyboardBuilder()
        reply_keyboard_builder.row(
            KeyboardButton(text="Создать анкету")
        )

        await message_source.answer(
            "Ваша анкета не найдена. Создайте ее сейчас:",
            reply_markup=reply_keyboard_builder.as_markup(resize_keyboard=True)
        )


@router.callback_query(F.data == "my_profile")
async def show_profile_from_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловит нажатие ИНЛАЙН-КНОПКИ "Моя анкета".
    """
    await _show_profile_logic(callback, state)


@router.message(F.text == "Моя анкета")
async def show_profile_from_text_button(message: types.Message, state: FSMContext):
    """
    Ловит текстовое сообщение "Моя анкета" от Reply-клавиатуры.
    """
    await _show_profile_logic(message, state)


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


@router.callback_query(F.data == "edit_age")
async def ask_for_age(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Возраст' и запрашивает новый возраст."""
    await callback.answer()
    await state.set_state(ProfileStates.filling_age)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Введите ваш новый возраст.**\n\n"
        "Возраст должен быть целым числом (от 0 до 100).",
        parse_mode='Markdown',
        reply_markup=back_button
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


@router.callback_query(F.data == "edit_level")
async def start_editing_level(callback: types.CallbackQuery, state: FSMContext):
    """
    Срабатывает при нажатии на 'Уровень владения', получает список инструментов
    и предлагает пользователю выбрать, какой инструмент редактировать.
    """
    await callback.answer()
    user_id = callback.from_user.id
    user_obj = await get_user(user_id)

    if not user_obj or not user_obj.instruments:
        # Убедимся, что здесь есть кнопка "Назад"
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
    """Сохраняет ID инструмента и предлагает выбрать уровень с помощью вербальной клавиатуры."""
    await callback.answer()

    instrument_id = int(callback.data.split(":")[1])
    # Сохраняем ID, который будем обновлять
    await state.update_data(current_instrument_id=instrument_id)
    # Переводим в состояние ожидания выбора уровня
    await state.set_state(ProfileStates.filling_level)
    # Создаем вербальную клавиатуру
    markup = get_level_rating_keyboard_verbal(instrument_id)

    await callback.message.edit_text(
        "**Выберите ваш уровень владения инструментом:**",
        parse_mode='Markdown',
        reply_markup=markup
    )


@router.callback_query(F.data.startswith("set_level:"), ProfileStates.filling_level)
async def process_new_level_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор уровня владения инструментом через Inline-клавиатуру и сохраняет его."""
    await callback.answer()

    #Извлекаем данные: instrument_id и new_level
    parts = callback.data.split(":")
    instrument_id = int(parts[1])
    new_level = int(parts[2])  # Здесь мы получаем числовой уровень от 1 до 5

    #Обновляем уровень в БД
    try:
        await update_instrument_level(instrument_id, new_level)
    except Exception as e:
        return

    #Завершаем FSM-шаг
    await state.set_state(ProfileStates.select_param_to_fill)

    #Возвращаем обновленный профиль с сообщением об успехе
    await send_updated_profile(
        callback,
        callback.from_user.id,
        success_message=f"Уровень владения инструментом успешно обновлен до **{new_level}**!"
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


@router.callback_query(F.data == "edit_experience")
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
        selected_experience = PerformanceExperience[experience_name]
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


@router.callback_query(F.data == "edit_theory")
async def start_selecting_theory_level(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Уровень теории' и показывает клавиатуру с вербальными градациями."""
    await callback.answer()
    await state.set_state(ProfileStates.selecting_theory_level)
    await callback.message.edit_text(
        "**Выберите ваш уровень теоретических знаний:**",
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


@router.callback_query(F.data == "edit_files")
async def start_uploading_files(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Загрузка файлов' и переводит в режим ожидания ОДНОГО аудио/ГС."""
    await callback.answer()
    await state.set_data({})
    await state.set_state(ProfileStates.uploading_files)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Пришлите аудиофайл или запишите голосовое сообщение**, чтобы продемонстрировать ваш уровень. \n\n"
        "Ваш файл заменит текущий демо-трек.",
        parse_mode='Markdown',
        reply_markup=back_button
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


@router.callback_query(F.data == "edit_link")
async def start_filling_link(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Ссылка' и переводит в режим ожидания URL."""
    await callback.answer()
    await state.set_state(ProfileStates.filling_external_link)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Пришлите ссылку на ваш плеер** (например, ЯндексМузыка, VK Музыка, YouTube и т.д.).\n\n"
        "Эта ссылка заменит текущую.",
        parse_mode='Markdown',
        reply_markup=back_button
    )


@router.callback_query(F.data == "edit_photo")
async def start_uploading_photo(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Фото' и переводит в режим ожидания ОДНОЙ фотографии."""
    await callback.answer()
    await state.set_state(ProfileStates.uploading_profile_photo)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Загрузите фотографию для вашего профиля.**\n\n",
        parse_mode='Markdown',
        reply_markup=back_button
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

@router.callback_query(F.data == "back_to_params")
async def process_back_to_params(callback: types.CallbackQuery, state: FSMContext):
    """
    Универсальный хендлер для возврата в меню выбора параметров профиля (ProfileStates.select_param_to_fill).
    """
    await callback.answer()

    # Сбрасываем текущее состояние на основное состояние редактирования
    await state.set_state(ProfileStates.select_param_to_fill)

    await callback.message.edit_text(
        "**Вы вернулись в меню редактирования.**\n\n"
        "Выберите следующий параметр для изменения:",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "back_to_params")
async def process_back_to_params(callback: types.CallbackQuery, state: FSMContext):
    """
    Универсальный хендлер для возврата в меню выбора параметров профиля.
    Возвращает полную анкету с клавиатурой редактирования.
    """
    await callback.answer()

    # Сбрасываем текущее состояние на основное состояние редактирования
    await state.set_state(ProfileStates.select_param_to_fill)

    user_id = callback.from_user.id

    # Вызываем функцию, которая заново загрузит данные, отправит медиа
    # и отправит обновленную текстовую анкету с клавиатурой get_profile_selection_keyboard().
    # Мы передаем 'callback', чтобы функция могла удалить/редактировать старое сообщение.
    await send_updated_profile(
        callback,
        user_id,
        success_message="Вы отменили текущее действие."
    )

@router.callback_query(F.data == "edit_name")
async def ask_for_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.filling_name)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Введите ваше новое имя:**",
        parse_mode='Markdown',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_name, F.text)
async def process_new_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text.strip()

    try:
        await update_user_name(user_id, new_name)  # метод из Registration
    except Exception as e:
        print(f"Ошибка сохранения имени в БД: {e}")
        await message.answer("Произошла ошибка при сохранении имени. Пожалуйста, попробуйте позже.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    await message.answer(
        f"**Имя успешно обновлено!**\n\n"
        f"Ваше новое имя: **{new_name}**.",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data == "edit_city")
async def ask_for_city(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.filling_city)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Введите ваш новый город:**",
        parse_mode='Markdown',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_city, F.text)
async def process_new_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_city = message.text.strip().lower()

    try:
        await update_user_city(user_id, new_city)
    except Exception as e:
        print(f"Ошибка сохранения города в БД: {e}")
        await message.answer("Произошла ошибка при сохранении города. Пожалуйста, попробуйте позже.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    await message.answer(
        f"**Город успешно обновлен!**\n\n"
        f"Ваш новый город: **{new_city}**.",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data == "edit_genres")
async def start_editing_genres(callback: types.CallbackQuery, state: FSMContext):
    """
    Запускает процесс выбора жанров для редактирования: загружает текущие жанры,
    инициализирует FSMContext и отправляет клавиатуру.
    """
    user_id = callback.from_user.id
    await callback.answer("Запуск редактирования жанров...")
    try:
        user_obj = await get_user(user_id)
        current_genres = user_obj.genres if user_obj and user_obj.genres else []
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
        await callback.message.edit_text("Ошибка при загрузке профиля. Попробуйте позже.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    standard_options = ["Рок", "Поп рок", "Гранж", "Метал", "Ню метал", "Панк"]
    selected_genres = [g for g in current_genres if g in standard_options]
    own_genres = [g for g in current_genres if g not in standard_options]

    await state.update_data(user_choice_genre=selected_genres)
    await state.update_data(own_user_genre=own_genres)

    msg_text = "**Выберите жанры**, в которых вы играете (они заменят текущие):"

    markup = make_keyboard_for_genre(selected_genres)

    await callback.message.edit_text(
        text=msg_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

    await state.set_state(RegistrationStates.genre)

@router.callback_query(F.data == "edit_instruments")
async def start_editing_instruments(callback: types.CallbackQuery, state: FSMContext):
    """
    Запускает процесс выбора инструментов, используя существующие функции make_keyboard_for_instruments.
    """
    await callback.answer()

    user_obj = await get_user(callback.from_user.id)
    current_instruments = user_obj.instruments if user_obj and user_obj.instruments else []

    # Разделение текущих инструментов на стандартные и собственные
    all_current_inst_names = [inst.name for inst in current_instruments]
    standard_options = ["Гитара", "Барабаны", "Синтезатор", "Вокал", "Бас", "Скрипка"]

    selected_inst = [name for name in all_current_inst_names if name in standard_options]
    own_inst = [name for name in all_current_inst_names if name not in standard_options]

    await state.update_data(user_choice_inst=selected_inst)
    await state.update_data(own_user_inst=own_inst)

    msg_text = "**Выберите инструмент/инструменты**, которыми вы владеете (они заменят текущие):"

    markup = make_keyboard_for_instruments(selected_inst)

    await callback.message.edit_text(text=msg_text, reply_markup=markup, parse_mode='Markdown')
    await state.set_state(
        RegistrationStates.instrument)

@router.callback_query(F.data == "edit_link")
async def start_filling_link(callback: types.CallbackQuery, state: FSMContext):
    """Срабатывает при нажатии на 'Ссылка' и переводит в режим ожидания URL."""
    await callback.answer()
    await state.set_state(ProfileStates.filling_external_link)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "**Пришлите ссылку на ваш плеер** (например, ЯндексМузыка, VK Музыка, YouTube и т.д.).\n\n"
        "Эта ссылка заменит текущую.",
        parse_mode='Markdown',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_external_link, F.text)
async def process_external_link(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_link = message.text.strip()

    try:
        await update_user(user_id=user_id, external_link=new_link)
    except Exception as e:
        print(f"Ошибка сохранения ссылки в БД: {e}")
        await message.answer("Произошла ошибка при сохранении ссылки. Пожалуйста, попробуйте позже.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    await message.answer(
        f"**Внешняя ссылка успешно обновлена!**\n\n"
        f"Ваша новая ссылка: **{new_link}**.",
        reply_markup=get_profile_selection_keyboard(),
        parse_mode='Markdown'
    )

def make_keyboard_for_genre(selected):
    """Клавиатура для жанров. Адаптирована для режима редактирования."""
    genres = ["Рок", "Поп рок", "Гранж", "Метал", "Ню метал", "Панк", "Свой вариант"]

    buttons = []
    for genre in genres:
        text = f"✅ {genre}" if genre in selected else genre
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"genre_{genre}")])

    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done_genres")])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_params")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "edit_genres")
async def start_editing_genres(callback: types.CallbackQuery, state: FSMContext):
    """Инициализирует FSMContext текущими жанрами пользователя и запускает выбор."""

    user_id = callback.from_user.id
    await callback.answer("Запуск редактирования жанров...")

    user_obj = await get_user(user_id)
    current_genres = user_obj.genres if user_obj and user_obj.genres else []

    standard_options = ["Рок", "Поп рок", "Гранж", "Метал", "Ню метал", "Панк"]
    selected_genres = [g for g in current_genres if g in standard_options]
    own_genres = [g for g in current_genres if g not in standard_options]

    await state.update_data(user_choice_genre=selected_genres)
    await state.update_data(own_user_genre=own_genres)

    markup = make_keyboard_for_genre(selected_genres)

    await callback.message.edit_text(
        text="**Выберите жанры**, в которых вы играете (они заменят текущие):",
        reply_markup=markup,
        parse_mode='Markdown'
    )

    await state.set_state(RegistrationStates.genre)

@router.callback_query(F.data.startswith("genre_"), RegistrationStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка клавиатуры для жанров"""
    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        back_button = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_params")]])

        await callback.message.edit_text(
            text="Напишите жанр:",
            reply_markup=back_button
        )
        await state.set_state(RegistrationStates.own_genre)
        return

    # Логика выбора/снятия выбора
    if choose in user_choice:
        user_choice.remove(choose)
    else:
        user_choice.append(choose)

    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_genre(user_choice)
    )
    await state.update_data(user_choice_genre=user_choice)

@router.message(F.text, RegistrationStates.own_genre)
async def own_genre(message: types.Message, state: FSMContext):
    """Обработка кнопки свой вариант для жанров. Сохраняем собственный жанр."""
    new_genre = message.text
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)

    msg_text = (f"Свой вариант: {', '.join(own_user_genre)}\n"
                "Отлично! Теперь выберите жанры в которых вы играете:")

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice))
    await state.set_state(RegistrationStates.genre)

@router.callback_query(F.data == "done_genres", RegistrationStates.genre)
async def done_genres(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки готово для жанров. Сохранение и возврат в профиль."""
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
        await update_user_genres(user_id, all_genres_user)
    except Exception as e:
        logger.error(f"Ошибка при сохранении жанров: {e}")
        await state.set_state(ProfileStates.select_param_to_fill)
        await send_updated_profile(callback, user_id, success_message="Произошла ошибка при сохранении жанров. Попробуйте позже.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    await send_updated_profile(
        callback,
        user_id,
        success_message="Жанры успешно обновлены!"
    )