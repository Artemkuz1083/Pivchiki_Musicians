import html
import logging

from aiogram import types, Router, F
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database.enums import PerformanceExperience
from database.queries import update_user, update_instrument_level, update_user_experience, update_user_theory_level, \
    save_user_profile_photo, save_user_audio, get_user, update_user_city, update_user_name, update_user_genres, \
    update_user_instruments, update_user_about_me, update_user_contacts
from handlers.enums.genres import Genre
from handlers.enums.instruments import Instruments
from handlers.profile.profile_keyboards import get_instrument_selection_keyboard, get_experience_selection_keyboard, \
    get_profile_selection_keyboard, get_edit_instruments_keyboard, get_theory_level_keyboard_verbal, \
    get_theory_level_keyboard_emoji, get_proficiency_star_keyboard, rating_to_stars, make_keyboard_for_genre, \
    make_keyboard_for_city
from states.states_profile import ProfileStates
from utils.analytics import track_event

logger = logging.getLogger(__name__)

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

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        try:
            await message.message.delete()
        except Exception:
            pass

    if success_message:
        await bot.send_message(chat_id, f"✅ {success_message}")

    try:
        user_obj = await get_user(user_id)
    except Exception as e:
        logger.error("Ошибка при получении данных пользователя %s в send_updated_profile: %s", user_id, e)
        await bot.send_message(chat_id, "⚠️ Произошла ошибка при доступе к профилю.")
        return

    if not user_obj:
        await bot.send_message(chat_id, "⚠️ Ваша анкета не найдена.")
        return

    # Подготовка данных
    name = html.escape(user_obj.name) if user_obj.name else "Не указано"
    city = html.escape(user_obj.city) if user_obj.city else "Не указано"
    age = user_obj.age if user_obj.age else "Не указано"
    contacts = html.escape(user_obj.contacts) if user_obj.contacts else "Не указано"

    knowledge_level = user_obj.theoretical_knowledge_level if user_obj.theoretical_knowledge_level is not None else 0
    stars_knowledge = rating_to_stars(knowledge_level)

    experience_display = getattr(user_obj.has_performance_experience, 'value', 'Не указано')

    genres_list = user_obj.genres or []
    genre_names = [html.escape(g.name) for g in genres_list]
    genres_display = ", ".join([f"#{g}" for g in genre_names]) if genre_names else "Не указано"

    instruments_lines = []
    if user_obj.instruments:
        for instrument in user_obj.instruments:
            proficiency_level = instrument.proficiency_level if instrument.proficiency_level is not None else 0
            stars_proficiency = rating_to_stars(proficiency_level)
            instruments_lines.append(
                f"  • <b>{html.escape(instrument.name)}</b>: {stars_proficiency}"
            )
        instruments_display = "\n".join(instruments_lines)
    else:
        instruments_display = "Не указаны"

    about_me_display = html.escape(user_obj.about_me) if user_obj.about_me else "Не указано"

    external_link_raw = user_obj.external_link
    if external_link_raw:
        external_link_display = f"<a href='{external_link_raw}'>🔗 Ссылка на портфолио</a>"
    else:
        external_link_display = "Не указана"

    # Формирование красивого текста
    profile_text = (
        f"📝 <b>Ваша обновленная анкета</b>\n"
        f"<i>Чтобы перейти в меню, напишите /start</i>\n\n"

        f"👤 <b>Имя:</b> {name}\n"
        f"🎂 <b>Возраст:</b> {age}\n"
        f"🏙 <b>Город:</b> {city}\n\n"

        f"💬 <b>О себе:</b>\n"
        f"<i>{about_me_display}</i>\n\n"

        f"🧠 <b>Музыкальная теория:</b> {stars_knowledge}\n"
        f"🎤 <b>Опыт выступлений:</b> {experience_display}\n\n"

        f"{external_link_display}\n\n"
        f"📞 <b>Контакты:</b> {html.escape(contacts)}\n\n"

        f"🎶 <b>Жанры:</b>\n{genres_display}\n\n"

        f"🎹 <b>Инструменты:</b>\n"
        f"{instruments_display}\n"
    )

    if user_obj.photo_path:
        try:
            await bot.send_photo(chat_id, photo=user_obj.photo_path, caption="📸 <b>Фото профиля</b>", parse_mode="HTML")
            logger.info("Пользователю %s отправлено фото профиля", user_id)
        except Exception as e:
            logger.error("Ошибка отправки фото по file_id для %s: %s", user_id, e)
            await bot.send_message(chat_id, "⚠️ Фото профиля не удалось загрузить.")

    if user_obj.audio_path:
        try:
            await bot.send_audio(chat_id, audio=user_obj.audio_path, caption="🎧 <b>Демо-трек</b>", parse_mode="HTML")
            logger.info("Пользователю %s демо-трек", user_id)
        except Exception as e:
            logger.error("Ошибка отправки аудио по file_id для %s: %s", user_id, e)
            await bot.send_message(chat_id, "⚠️ Демо-трек не удалось загрузить.")

    username = message.from_user.username
    keyboard = get_profile_selection_keyboard(user_id, username)

    try:
        await bot.send_message(
            chat_id,
            profile_text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        logger.info("Пользователю %s отправлена обновленная анкета", user_id)
    except Exception as e:
        logger.error("Ошибка отправки профиля пользователю %s: %s", user_id, e)
        # Fallback (упрощенный текст)
        simple_text = (
            f"<b>Ваша анкета</b>\n\n"
            f"Имя: {name}\n"
            f"Город: {city}\n"
            f"Инструменты: {len(user_obj.instruments) if user_obj.instruments else 0}"
        )
        await bot.send_message(chat_id, simple_text, reply_markup=keyboard, parse_mode="HTML")


async def _show_profile_logic(event: types.Message | types.CallbackQuery, state: FSMContext):
    """Универсальная логика для показа анкеты."""
    user_id = event.from_user.id
    logger.info("Пользователь %s запросил свою анкету", user_id)
    await track_event(user_id, "profile_view")

    if isinstance(event, types.CallbackQuery):
        await event.answer()
        message_source = event.message
    else:
        message_source = event

    try:
        user_obj = await get_user(user_id)
    except Exception as e:
        logger.error("Ошибка при получении данных пользователя %s: %s", user_id, e)
        await message_source.answer("⚠️ Произошла ошибка при доступе к профилю.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)

    if user_obj:
        await send_updated_profile(event, user_id)
    else:
        logger.warning("Анкета пользователя %s не найдена, предлагаем регистрацию", user_id)
        reply_keyboard_builder = ReplyKeyboardBuilder()
        reply_keyboard_builder.row(KeyboardButton(text="Let's go 🚀"))

        await message_source.answer(
            "😞 <b>Ваша анкета не найдена.</b>\nСоздайте её прямо сейчас:",
            reply_markup=reply_keyboard_builder.as_markup(resize_keyboard=True),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "my_profile")
async def show_profile_from_callback(callback: types.CallbackQuery, state: FSMContext):
    await _show_profile_logic(callback, state)


@router.message(F.text == "👤 Моя анкета")
async def show_profile_from_text_button(message: types.Message, state: FSMContext):
    await _show_profile_logic(message, state)


@router.callback_query(F.data == "fill_profile")
async def start_filling_profile(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s перешел в режим редактирования профиля", user_id)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(ProfileStates.select_param_to_fill)

    username = callback.from_user.username

    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="⚙️ <b>Редактирование профиля</b>\nВыберите параметр, который хотите изменить:",
        reply_markup=get_profile_selection_keyboard(user_id, username),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "edit_age")
async def ask_for_age(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование возраста", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.filling_age)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "🎂 <b>Введите ваш новый возраст.</b>\n\n"
        "<i>(Только целое число от 0 до 100)</i>",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_age, F.text)
async def process_new_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_age_str = message.text.strip()
    try:
        new_age = int(new_age_str)
        if not (0 <= new_age <= 100):
            raise ValueError("Возраст вне диапазона")
    except ValueError:
        logger.warning("Пользователь %s ввел неверный возраст: %s", user_id, new_age_str)
        await message.answer(
            "⚠️ <b>Неверный ввод.</b>\nПожалуйста, введите возраст как целое число от 0 до 100."
        )
        return

    try:
        await update_user(user_id=user_id, age=new_age)
        logger.info("Пользователь %s обновил возраст на %d", user_id, new_age)
    except Exception as e:
        logger.error("Ошибка сохранения возраста пользователя %s: %s", user_id, e)
        await message.answer("⚠️ Ошибка сохранения. Попробуйте позже.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(message, user_id, success_message=f"Возраст обновлен: <b>{new_age}</b>")


@router.callback_query(F.data == "edit_level")
async def start_editing_level(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    logger.info("Пользователь %s начал редактирование уровня владения инструментами", user_id)
    await callback.answer()
    user_obj = await get_user(user_id)

    if not user_obj or not user_obj.instruments:
        logger.warning("Пользователь %s пытался редактировать уровень, не имея инструментов", user_id)
        await callback.message.edit_text(
            "⚠️ <b>У вас пока нет инструментов.</b>\nСначала добавьте их в разделе 'Инструменты'.",
            reply_markup=get_profile_selection_keyboard(user_id, username),
            parse_mode="HTML"
        )
        return

    instrument_keyboard = get_instrument_selection_keyboard(user_obj.instruments)
    await state.set_state(ProfileStates.select_instrument_to_edit)

    await callback.message.edit_text(
        "🎹 <b>Уровень владения</b>\n"
        "Выберите инструмент, уровень владения которым вы хотите изменить:",
        reply_markup=instrument_keyboard,
        parse_mode='HTML'
    )


@router.callback_query(F.data == "edit_theory")
async def start_selecting_theory_level_emoji(callback: types.CallbackQuery, state: FSMContext):
    """Версия с эмодзи (звездами)"""
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование уровня муз. теории", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.selecting_theory_level)

    await callback.message.edit_text(
        "🧠 <b>Теоретические знания</b>\n"
        "Выберите ваш уровень:",
        reply_markup=get_theory_level_keyboard_emoji(),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith("set_level:"), ProfileStates.filling_level)
async def process_new_level_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    parts = callback.data.split(":")
    instrument_id = int(parts[1])
    new_level = int(parts[2])

    try:
        await update_instrument_level(instrument_id, new_level)
        logger.info("Пользователь %s обновил уровень инструмента ID=%d до %d", user_id, instrument_id, new_level)
    except Exception as e:
        logger.error("Ошибка обновления уровня инструмента ID=%d для %s: %s", instrument_id, user_id, e)
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(
        callback,
        user_id,
        success_message=f"Уровень владения обновлен до {rating_to_stars(new_level)}!"
    )


@router.callback_query(F.data.startswith("edit_instrument_level:"), ProfileStates.select_instrument_to_edit)
async def select_instrument_for_level_edit(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    try:
        parts = callback.data.split(":")
        instrument_id = int(parts[1])
        instrument_name = parts[2].replace("_", " ")
    except (IndexError, ValueError) as e:
        logger.error("Ошибка при разборе ID инструмента от %s: %s", user_id, e)
        await callback.message.edit_text("⚠️ Ошибка выбора инструмента.")
        return

    logger.info("Пользователь %s выбрал инструмент '%s' (ID=%d) для оценки уровня", user_id, instrument_name,
                instrument_id)
    await state.set_state(ProfileStates.filling_level)

    await callback.message.edit_text(
        f"🎸 Инструмент: <b>{instrument_name}</b>\n\n"
        f"Выберите ваш новый уровень владения:",
        reply_markup=get_proficiency_star_keyboard(instrument_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "edit_experience")
async def start_editing_experience(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование опыта выступлений", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.selecting_experience_type)
    await callback.message.edit_text(
        "🎤 <b>Опыт выступлений</b>\n"
        "Выберите подходящий вариант:",
        reply_markup=get_experience_selection_keyboard(),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith("select_exp:"), ProfileStates.selecting_experience_type)
async def process_experience_type(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    experience_name = callback.data.split(":")[1]

    try:
        selected_experience = PerformanceExperience[experience_name]
    except KeyError:
        logger.error("Неизвестный тип опыта '%s' от пользователя %s", experience_name, user_id)
        await callback.message.edit_text("⚠️ Ошибка выбора.")
        return

    try:
        await update_user_experience(user_id, selected_experience)
        logger.info("Пользователь %s обновил опыт выступлений на: %s", user_id, selected_experience.value)
    except Exception as e:
        logger.error("Ошибка сохранения опыта выступлений для %s: %s", user_id, e)

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()

    await send_updated_profile(
        callback,
        user_id,
        success_message=f"Опыт выступлений обновлен: <b>{selected_experience.value}</b>"
    )


# Дублирующая функция для теории (текстовая), если используется она
@router.callback_query(F.data == "edit_theory_text")
async def start_selecting_theory_level_text(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование уровня муз. теории (текст)", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.selecting_theory_level)
    await callback.message.edit_text(
        "🧠 <b>Теоретические знания</b>\n"
        "Выберите ваш уровень:",
        reply_markup=get_theory_level_keyboard_verbal(),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith("set_theory_level:"), ProfileStates.selecting_theory_level)
async def process_selected_theory_level(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    try:
        new_level = int(callback.data.split(":")[1])
    except ValueError:
        logger.error("Неверный уровень теории от пользователя %s: %s", user_id, callback.data)
        return

    try:
        await update_user_theory_level(user_id=user_id, theory_level=new_level)
        logger.info("Пользователь %s обновил уровень теории на %d", user_id, new_level)
    except Exception as e:
        logger.error("Ошибка сохранения уровня теории для %s: %s", user_id, e)

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()

    await send_updated_profile(
        callback,
        user_id,
        success_message=f"Уровень теории обновлен: <b>{new_level}</b>"
    )


@router.callback_query(F.data == "edit_files")
async def start_uploading_files(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал загрузку аудио/демо", user_id)
    await callback.answer()
    await state.set_data({})
    await state.set_state(ProfileStates.uploading_files)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "🎧 <b>Аудио / Голосовое</b>\n\n"
        "Пришлите аудиофайл или запишите голосовое сообщение.\n"
        "<i>Этот файл заменит текущий демо-трек.</i>",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.uploading_files, F.audio | F.voice)
async def handle_uploaded_audio_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_id = None
    content_type = "аудио"

    if message.audio:
        file_id = message.audio.file_id
        content_type = "аудиофайл"
    elif message.voice:
        file_id = message.voice.file_id
        content_type = "голосовое сообщение"

    if file_id:
        try:
            await save_user_audio(user_id=user_id, file_id=file_id)
            logger.info("Пользователь %s обновил демо-трек (%s)", user_id, content_type)
            await track_event(user_id, "profile_update_audio", {"type": content_type})
        except Exception as e:
            logger.error("Ошибка сохранения аудио от %s: %s", user_id, e)
            await message.answer("⚠️ Ошибка сохранения. Попробуйте позже.")
            return

        await state.set_state(ProfileStates.select_param_to_fill)
        await state.clear()

        await send_updated_profile(message, user_id, success_message=f"Демо ({content_type}) обновлено!")


@router.callback_query(F.data == "edit_photo")
async def start_uploading_photo(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал загрузку фото", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.uploading_profile_photo)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "📸 <b>Фото профиля</b>\n\n"
        "Отправьте фотографию, которую хотите установить в анкету.",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.uploading_profile_photo, F.photo)
async def handle_uploaded_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    photo_file_id = message.photo[-1].file_id
    try:
        await save_user_profile_photo(user_id=user_id, file_id=photo_file_id)
        logger.info("Пользователь %s обновил фото профиля", user_id)
        await track_event(user_id, "profile_update_photo")
    except Exception as e:
        logger.error("Ошибка сохранения фото от %s: %s", user_id, e)
        await message.answer("⚠️ Ошибка сохранения фото.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await state.clear()

    await send_updated_profile(message, user_id, success_message="Фотография профиля обновлена!")


@router.callback_query(F.data == "back_to_params")
async def process_back_to_params(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s вернулся в меню параметров редактирования", user_id)
    await callback.answer("Отмена")
    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(callback, user_id, success_message="Действие отменено.")


@router.callback_query(F.data == "edit_name")
async def ask_for_name(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование имени", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.filling_name)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "👤 <b>Введите ваше новое имя:</b>",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_name, F.text)
async def process_new_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text.strip()

    try:
        await update_user_name(user_id, new_name)
        logger.info("Пользователь %s обновил имя на: %s", user_id, new_name)
    except Exception as e:
        logger.error("Ошибка сохранения имени от %s: %s", user_id, e)
        await message.answer("⚠️ Ошибка сохранения.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(message, user_id, success_message=f"Имя обновлено: <b>{html.escape(new_name)}</b>")


@router.callback_query(F.data == "edit_city")
async def start_city_editing(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_obj = await get_user(user_id)  # Получаем текущего пользователя из БД

    # Извлекаем текущие города из строки в список
    current_cities = []
    if user_obj and user_obj.city:
        current_cities = [c.strip() for c in user_obj.city.split(",") if c.strip()]

    # Сохраняем список в стейт для временного хранения
    await state.update_data(temp_selected_cities=current_cities)
    await state.set_state(ProfileStates.filling_city)

    await callback.message.edit_text(
        "🏙 <b>Выберите города, в которых вы готовы играть:</b>\n"
        "<i>Можно выбрать несколько вариантов.</i>",
        reply_markup=make_keyboard_for_city(current_cities),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("city_"), ProfileStates.filling_city)
async def toggle_city_selection(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[1]

    if city == "own":
        await callback.message.edit_text("🏙 <b>Введите название города текстом:</b>")
        await state.set_state(ProfileStates.own_city)
        return

    # Получаем текущий временный список
    data = await state.get_data()
    selected = data.get("temp_selected_cities", [])

    # Переключаем (Toggle): если есть — удаляем, если нет — добавляем
    if city in selected:
        selected.remove(city)
    else:
        selected.append(city)

    await state.update_data(temp_selected_cities=selected)

    # Обновляем только клавиатуру, не перерисовывая всё сообщение
    await callback.message.edit_reply_markup(
        reply_markup=make_keyboard_for_city(selected)
    )
    await callback.answer()


@router.callback_query(F.data == "done_cities", ProfileStates.filling_city)
async def finish_city_editing(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    selected = data.get("temp_selected_cities", [])

    if not selected:
        await callback.answer("⚠️ Выберите хотя бы один город!", show_alert=True)
        return

    # Склеиваем список обратно в строку для БД
    cities_string = ", ".join(selected)

    await update_user_city(user_id, cities_string)  # Ваша функция обновления БД

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(callback, user_id, success_message=f"✅ Города обновлены: {cities_string}")
    await callback.answer()


@router.callback_query(F.data == "edit_instruments")
async def start_editing_instruments(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование инструментов", user_id)
    await callback.answer()

    user_obj = await get_user(user_id)
    current_instruments = user_obj.instruments if user_obj and user_obj.instruments else []
    all_current_inst_names = [inst.name for inst in current_instruments]
    standard_options = Instruments.list_values()

    selected_inst = [name for name in all_current_inst_names if name in standard_options]
    own_inst = [name for name in all_current_inst_names if name not in standard_options]

    await state.update_data(user_choice_inst=selected_inst, own_user_inst=own_inst)

    msg_text = (
        "🎸 <b>Инструменты</b>\n"
        "Выберите инструменты, которыми вы владеете.\n"
        "<i>Нажмите 'Свой вариант' для ввода текста.</i>"
    )
    markup = get_edit_instruments_keyboard(selected_inst)

    await callback.message.edit_text(text=msg_text, reply_markup=markup, parse_mode='HTML')
    await state.set_state(ProfileStates.instrument_edit)


@router.callback_query(F.data.startswith("edit_inst_"), ProfileStates.instrument_edit)
async def process_instrument_selection_in_edit(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    instrument_name = callback.data.split("_", 2)[2]
    data = await state.get_data()
    selected_inst: list = data.get("user_choice_inst", [])

    action = ""
    if instrument_name in selected_inst:
        selected_inst.remove(instrument_name)
        action = "удалил"
    else:
        selected_inst.append(instrument_name)
        action = "добавил"

    logger.info("Пользователь %s %s стандартный инструмент: %s", user_id, action, instrument_name)
    await state.update_data(user_choice_inst=selected_inst)
    markup = get_edit_instruments_keyboard(selected_inst)

    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@router.callback_query(F.data == "input_own_instrument", ProfileStates.instrument_edit)
async def ask_for_own_instrument(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s запросил ввод собственного инструмента", user_id)
    await callback.answer()
    await callback.message.edit_text(
        "📝 <b>Введите название инструмента:</b>",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.instrument_edit)


@router.message(ProfileStates.instrument_edit, F.text)
async def process_own_instrument_in_edit(message: types.Message, state: FSMContext):
    new_instrument_name = message.text.strip()
    user_id = message.from_user.id
    data = await state.get_data()

    own_inst: list = data.get("own_user_inst", [])
    selected_inst: list = data.get("user_choice_inst", [])

    if new_instrument_name in selected_inst or new_instrument_name in own_inst:
        logger.warning("Пользователь %s попытался добавить уже существующий инструмент: %s", user_id,
                       new_instrument_name)
        await message.answer("⚠️ Этот инструмент уже добавлен. Введите другой или нажмите 'Готово'.")
        return

    own_inst.append(new_instrument_name)
    await state.update_data(own_user_inst=own_inst)
    logger.info("Пользователь %s добавил собственный инструмент: %s. Всего своих: %d", user_id, new_instrument_name,
                len(own_inst))

    markup = get_edit_instruments_keyboard(selected_inst)

    await message.answer(
        f"✅ Инструмент <b>{html.escape(new_instrument_name)}</b> добавлен.\n"
        "Продолжайте выбирать или нажмите 'Готово':",
        reply_markup=markup,
        parse_mode='HTML'
    )
    await state.set_state(ProfileStates.instrument_edit)


async def _send_level_selection_menu(callback: types.CallbackQuery, state: FSMContext, user_id: int):
    user_obj = await get_user(user_id)
    username = callback.from_user.username

    if not user_obj or not user_obj.instruments:
        logger.error("Инструменты не найдены для пользователя %s после сохранения.", user_id)
        await callback.message.edit_text(
            "⚠️ Инструменты не найдены.",
            reply_markup=get_profile_selection_keyboard(user_id, username)
        )
        return

    instrument_keyboard = get_instrument_selection_keyboard(user_obj.instruments)
    await state.set_state(ProfileStates.select_instrument_to_edit)

    await callback.message.edit_text(
        "✅ <b>Инструменты сохранены!</b>\n\n"
        "🎹 Теперь выберите инструмент, чтобы указать <b>уровень владения</b>:",
        reply_markup=instrument_keyboard,
        parse_mode='HTML'
    )


@router.callback_query(F.data == "instruments_ready_edit", ProfileStates.instrument_edit)
async def finalize_instrument_editing(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer("Сохранение...")
    data = await state.get_data()

    selected_inst = data.get("user_choice_inst", [])
    own_inst = data.get("own_user_inst", [])
    all_instruments = selected_inst + own_inst

    logger.info("Пользователь %s завершает редактирование списка инструментов %s", user_id, all_instruments)

    try:
        await update_user_instruments(user_id, all_instruments)
        await track_event(user_id, "profile_update_instruments", {"count": len(all_instruments)})
        logger.info("Пользователь %s сохранил %d инструментов", user_id, len(all_instruments))
    except Exception as e:
        logger.error("Ошибка сохранения инструментов для %s: %s", user_id, e)
        await callback.message.answer("⚠️ Ошибка сохранения.")
        await state.set_state(ProfileStates.select_param_to_fill)
        return

    await _send_level_selection_menu(callback, state, user_id)


@router.callback_query(F.data == "edit_link")
async def start_filling_link(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование внешней ссылки", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.filling_external_link)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "🔗 <b>Внешняя ссылка</b>\n\n"
        "Пришлите ссылку на ваш плеер (Яндекс, VK, YouTube и т.д.).",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_external_link, F.text)
async def process_external_link(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_link = message.text.strip()

    try:
        await update_user(user_id=user_id, external_link=new_link)
        logger.info("Пользователь %s обновил внешнюю ссылку: %s", user_id, new_link)
        await track_event(user_id, "profile_update_link")
    except Exception as e:
        logger.error("Ошибка сохранения ссылки от %s: %s", user_id, e)
        await message.answer("⚠️ Ошибка сохранения ссылки.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(message, user_id, success_message="Ссылка успешно обновлена!")


# начало редактирования контактов
@router.callback_query(F.data == "edit_contacts")
async def edit_contacts(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование контактов", user_id)

    await callback.message.edit_text(
        "📞 <b>Введите новые контактные данные</b> (Telegram @username, телефон, email):\n\n",
        parse_mode="HTML"
    )

    await state.set_state(ProfileStates.edit_contacts)
    await callback.answer()


# сохранение новых контактов
@router.message(F.text, ProfileStates.edit_contacts)
async def save_new_contacts(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_contacts = message.text.strip()

    try:
        await update_user_contacts(user_id, new_contacts)
        logger.info("Пользователь ID=%s успешно обновил контакты", user_id)

        await state.set_state(None)

        await send_updated_profile(
            message,
            user_id,
            success_message="<b>Ваши контакты успешно обновлены!</b>"
        )
        await track_event(user_id, "profile_update_contacts")

    except Exception as e:
        logger.error("Ошибка обновления контактов для пользователя ID=%s: %s", user_id, e)
        await message.answer("⚠️ Произошла ошибка при сохранении контактов. Попробуйте еще раз.")
        await state.set_state(None)
        await send_updated_profile(message, user_id)


@router.callback_query(F.data == "edit_genres")
async def start_editing_genres(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование жанров", user_id)
    await callback.answer("Загрузка...")
    user_obj = await get_user(user_id)
    current_genre_names = [g.name for g in user_obj.genres] if user_obj and user_obj.genres else []

    standard_options = Genre.list_values()
    selected_genres = [name for name in current_genre_names if name in standard_options]
    own_genres = [name for name in current_genre_names if name not in standard_options]

    await state.update_data(user_choice_genre=selected_genres, own_user_genre=own_genres)

    markup = make_keyboard_for_genre(selected_genres)
    await callback.message.edit_text(
        text="🎶 <b>Жанры</b>\nВыберите жанры, в которых вы играете:",
        reply_markup=markup,
        parse_mode='HTML'
    )
    await state.set_state(ProfileStates.genre)


@router.callback_query(F.data.startswith("genre_"), ProfileStates.genre)
async def choose_genre(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    choose = callback.data.split("_")[1]
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])

    if choose == "Свой вариант":
        logger.info("Пользователь %s запросил ввод собственного жанра при редактировании", user_id)
        back_button = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

        await callback.message.edit_text(
            text="📝 <b>Напишите название жанра:</b>",
            reply_markup=back_button,
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.own_genre)
        return

    action = ""
    if choose in user_choice:
        user_choice.remove(choose)
        action = "удалил"
    else:
        user_choice.append(choose)
        action = "добавил"

    logger.info("Пользователь %s %s жанр: %s", user_id, action, choose)
    await state.update_data(user_choice_genre=user_choice)
    await callback.message.edit_reply_markup(reply_markup=make_keyboard_for_genre(user_choice))


@router.message(F.text, ProfileStates.own_genre)
async def own_genre(message: types.Message, state: FSMContext):
    new_genre = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    own_user_genre = data.get("own_user_genre", [])
    user_choice = data.get("user_choice_genre", [])

    own_user_genre.append(new_genre)
    await state.update_data(own_user_genre=own_user_genre)
    logger.info("Пользователь %s добавил собственный жанр: %s", user_id, new_genre)

    msg_text = (
        f"✅ Добавлен свой вариант: <b>{html.escape(new_genre)}</b>\n"
        "Выберите еще жанры или нажмите 'Готово':"
    )

    await message.answer(text=msg_text, reply_markup=make_keyboard_for_genre(user_choice), parse_mode="HTML")
    await state.set_state(ProfileStates.genre)


@router.callback_query(F.data == "done_genres", ProfileStates.genre)
async def done_genres(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    data = await state.get_data()
    user_choice = data.get("user_choice_genre", [])
    own_user_genre = data.get("own_user_genre", [])
    all_genres_user = user_choice + own_user_genre

    if not all_genres_user:
        logger.warning("Пользователь %s попытался сохранить пустой список жанров", user_id)
        await callback.message.answer("⚠️ Пожалуйста, выберите хотя бы один жанр.")
        return

    try:
        await update_user_genres(user_id, all_genres_user)
        await track_event(user_id, "profile_update_genres", {"count": len(all_genres_user)})
        logger.info("Пользователь %s сохранил %d жанров: %s", user_id, len(all_genres_user), all_genres_user)
    except Exception as e:
        logger.error("Ошибка сохранения жанров для %s: %s", user_id, e)
        await state.set_state(ProfileStates.select_param_to_fill)
        await send_updated_profile(callback, user_id, success_message="⚠️ Ошибка при сохранении.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(callback, user_id, success_message="Жанры успешно обновлены!")


@router.callback_query(F.data == "edit_about_me")
async def ask_for_about_me(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info("Пользователь %s начал редактирование 'О себе'", user_id)
    await callback.answer()
    await state.set_state(ProfileStates.filling_about_me)

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_params")]])

    await callback.message.edit_text(
        "💬 <b>О себе</b>\n\n"
        "Введите краткий рассказ о себе, своем творчестве и целях.",
        parse_mode='HTML',
        reply_markup=back_button
    )


@router.message(ProfileStates.filling_about_me, F.text)
async def process_new_about_me(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    about_me_text = message.text.strip()

    if len(about_me_text) > 1000:
        logger.warning("Пользователь %s ввел слишком длинный текст 'О себе'", user_id)
        await message.answer("⚠️ Текст слишком длинный (максимум 1000 символов).")
        return

    try:
        await update_user_about_me(user_id, about_me_text)
        await track_event(user_id, "profile_update_bio", {"length": len(about_me_text)})
        logger.info("Пользователь %s обновил раздел 'О себе'", user_id)
    except Exception as e:
        logger.error("Ошибка сохранения 'О себе' от %s: %s", user_id, e)
        await message.answer("⚠️ Ошибка сохранения.")
        return

    await state.set_state(ProfileStates.select_param_to_fill)
    await send_updated_profile(message, user_id, success_message="Раздел 'О себе' обновлен!")