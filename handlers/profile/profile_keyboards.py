from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from database.enums import PerformanceExperience
from handlers.enums.genres import Genre
from handlers.enums.instruments import Instruments


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
        encoded_name = instrument.name.replace(" ", "_")
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (ур. {instrument.proficiency_level})",
            callback_data=f"edit_instrument_level:{instrument.id}:{encoded_name}"
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

    builder.add(
        InlineKeyboardButton(text="Имя", callback_data="edit_name"),
        InlineKeyboardButton(text="Город", callback_data="edit_city"),
        InlineKeyboardButton(text="Жанры", callback_data="edit_genres"),
        InlineKeyboardButton(text="Инструменты", callback_data="edit_instruments"),
        InlineKeyboardButton(text="Возраст", callback_data="edit_age"),
        InlineKeyboardButton(text="Уровень владения", callback_data="edit_level"),
        InlineKeyboardButton(text="Опыт выступлений", callback_data="edit_experience"),
        InlineKeyboardButton(text="Уровень теории", callback_data="edit_theory"),
        InlineKeyboardButton(text="Демонстрационные файлы", callback_data="edit_files"),
        InlineKeyboardButton(text="Внешняя ссылка", callback_data="edit_link"),
        InlineKeyboardButton(text="Фото", callback_data="edit_photo"),
        InlineKeyboardButton(text="О себе", callback_data="edit_about_me"),
    )

    builder.adjust(2)
    #builder.row(InlineKeyboardButton(text="Назад", callback_data="back_from_profile"))
    return builder.as_markup()


def get_edit_instruments_keyboard(selected_instruments: list) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для выбора инструментов в режиме редактирования."""
    standard_instruments = Instruments.list_values()

    builder = InlineKeyboardBuilder()

    for inst in standard_instruments:
        text = f"✅ {inst}" if inst in selected_instruments else inst
        builder.row(InlineKeyboardButton(text=text, callback_data=f"edit_inst_{inst}"))

    builder.row(InlineKeyboardButton(text="Свой вариант (введите текстом)", callback_data="input_own_instrument"))

    builder.row(InlineKeyboardButton(text="✅ Готово (Перейти к оценке)", callback_data="instruments_ready_edit"))
    builder.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_params"))

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
    return builder.as_markup()


def get_theory_level_keyboard_emoji() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с градациями уровня теории в виде звезд.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="❌ (Не знаю теорию)", callback_data="set_theory_level:0")
    )

    builder.row(
        InlineKeyboardButton(text="⭐", callback_data="set_theory_level:1"),
        InlineKeyboardButton(text="⭐⭐", callback_data="set_theory_level:2")
    )

    builder.row(
        InlineKeyboardButton(text="⭐⭐⭐", callback_data="set_theory_level:3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="set_theory_level:4")
    )

    builder.row(
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="set_theory_level:5")
    )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_params")
    )

    return builder.as_markup()


def get_proficiency_star_keyboard(instrument_id: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с градациями уровня ВЛАДЕНИЯ (proficiency)
    в виде звезд (1-5) для конкретного instrument_id.
    """
    builder = InlineKeyboardBuilder()

    # "set_level:{instrument_id}:{new_level}"
    CALLBACK_PREFIX = f"set_level:{instrument_id}"

    builder.row(
        InlineKeyboardButton(text="⭐", callback_data=f"{CALLBACK_PREFIX}:1"),
        InlineKeyboardButton(text="⭐⭐", callback_data=f"{CALLBACK_PREFIX}:2")
    )

    builder.row(
        InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"{CALLBACK_PREFIX}:3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"{CALLBACK_PREFIX}:4")
    )

    builder.row(
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"{CALLBACK_PREFIX}:5")
    )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_params")
    )

    return builder.as_markup()


def rating_to_stars(level: int) -> str:
    if level is None:
        level = 0
    return "⭐️" * level


def get_edit_rating_keyboard(instruments: List) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру со списком инструментов пользователя для оценки уровня."""
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        # ✅ Уникальный колбэк, использует ID инструмента
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (Уровень: {instrument.proficiency_level or '?'})",
            callback_data=f"select_edit_inst:{instrument.id}"
        ))

    # ✅ Уникальный колбэк "Готово" для завершения
    builder.row(InlineKeyboardButton(text="✅ Готово (Профиль)", callback_data="rating_done_edit"))
    return builder.as_markup()


def make_keyboard_for_genre(selected: list[str]) -> InlineKeyboardMarkup:
    """Клавиатура для жанров. Адаптирована для режима редактирования."""

    # 1. Получаем стандартные жанры из Enum
    standard_genres = Genre.list_values()

    # 2. Добавляем опцию для ввода собственного жанра
    all_genre_options = standard_genres + ["Свой вариант"]

    buttons = []

    for genre in all_genre_options:
        # Для стандартных жанров проверяем, выбран ли он
        is_selected = genre in selected and genre in standard_genres

        # Специальная обработка текста для "Свой вариант" (если нужно, но в текущей логике не меняется)
        if genre == "Свой вариант":
            text = "Свой вариант 📝"
        else:
            text = f"✅ {genre}" if is_selected else genre
        callback_data = f"genre_{genre}"

        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Кнопки управления
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done_genres")])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_params")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
