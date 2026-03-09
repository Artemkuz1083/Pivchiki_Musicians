from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from database.enums import PerformanceExperience
from handlers.enums.cities import City
from handlers.enums.genres import Genre
from handlers.enums.instruments import Instruments

# клавиатура для редактирования профиля
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

# клавиатура со списком инструментов пользователя
def get_instrument_selection_keyboard(instruments: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        encoded_name = instrument.name.replace(" ", "_")
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (ур. {instrument.proficiency_level})",
            callback_data=f"edit_instrument_level:{instrument.id}:{encoded_name}"
        ))

    builder.row(InlineKeyboardButton(text="Назад", callback_data="back_to_params"))
    return builder.as_markup()

# клавиатура для вариантов опыта выступления
def get_experience_selection_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Итерируемся по Enum
    for exp_type in PerformanceExperience:
        builder.row(InlineKeyboardButton(
            text=exp_type.value,
            callback_data=f"select_exp:{exp_type.name}"
        ))

    builder.row(InlineKeyboardButton(text="Назад", callback_data="back_to_params"))

    return builder.as_markup()

# клавиатура для выбора параметров профиля
def get_profile_selection_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    WEB_APP_URL = "https://music-app.vercel.app"

    builder.row(InlineKeyboardButton(
        text="🔍 Открыть Web App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    ))

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
        InlineKeyboardButton(text="Контакты", callback_data="edit_contacts"),
        InlineKeyboardButton(text="Фото", callback_data="edit_photo"),
        InlineKeyboardButton(text="О себе", callback_data="edit_about_me"),
    )

    builder.adjust(1, 2)
    #builder.row(InlineKeyboardButton(text="Назад", callback_data="back_from_profile"))
    return builder.as_markup()


def get_edit_instruments_keyboard(selected_instruments: List[str]) -> InlineKeyboardMarkup:
    """
    Генерирует Inline-клавиатуру для выбора инструментов, используя adjust(2)
    для расположения стандартных вариантов в две колонки.
    """
    standard_instruments = Instruments.list_values()
    builder = InlineKeyboardBuilder()

    # 1. Добавляем кнопки для всех стандартных инструментов
    for inst in standard_instruments:
        text = f"✅ {inst}" if inst in selected_instruments else inst

        # Используем .button() для добавления кнопки в буфер
        builder.button(
            text=text,
            callback_data=f"edit_inst_{inst}"
        )

    # 2. Применяем adjust(2) для создания двух колонок из всех добавленных выше кнопок
    builder.adjust(2)

    # 3. Добавляем кнопки ввода своего варианта и управления
    # Эти кнопки будут размещены ПОСЛЕ автоматической сетки

    # Кнопка "Свой вариант" (занимает весь ряд)
    builder.row(
        InlineKeyboardButton(
            text="Свой вариант (введите текстом)",
            callback_data="input_own_instrument"
        )
    )

    # Кнопки "Готово" и "Назад" (расположены в одном ряду, по две)
    builder.row(
        InlineKeyboardButton(
            text="Назад в меню",
            callback_data="back_to_params"
        ),
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data="instruments_ready_edit"
        )
    )

    return builder.as_markup()

# клавиатура уровней теории
def get_theory_level_keyboard_verbal() -> InlineKeyboardMarkup:
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


# клавиатура для оценивания теории
def get_theory_level_keyboard_emoji() -> InlineKeyboardMarkup:
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

# клавиатура для уровня владения инструментов
def get_proficiency_star_keyboard(instrument_id: int) -> InlineKeyboardMarkup:
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

# клавиатура для оценивания инструментов
def get_edit_rating_keyboard(instruments: List) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (Уровень: {instrument.proficiency_level or '?'})",
            callback_data=f"select_edit_inst:{instrument.id}"
        ))

    builder.row(InlineKeyboardButton(text="✅ Готово (Профиль)", callback_data="rating_done_edit"))
    return builder.as_markup()

# клавиатура для жанров
def make_keyboard_for_genre(selected: list[str]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру жанров с выбором. Жанры расположены в две колонки.
    """
    standard_genres = Genre.list_values()
    buttons = []

    genre_options_list = []
    for genre in standard_genres:
        is_selected = genre in selected
        text = f"✅ {genre}" if is_selected else genre
        callback_data = f"genre_{genre}"
        genre_options_list.append(InlineKeyboardButton(text=text, callback_data=callback_data))

    #Группируем стандартные жанры по две
    for i in range(0, len(genre_options_list), 2):
        # Добавляем строку из двух или одной кнопки
        buttons.append(genre_options_list[i:i + 2])

    buttons.append([InlineKeyboardButton(text="Свой вариант 📝", callback_data="genre_Свой вариант")])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_params")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done_genres")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# клавиатура для выбора города
def make_keyboard_for_city(selected_cities: List[str]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру городов. Выбранные города помечаются галочкой.
    """
    standard_cities = City.list_values()
    builder = InlineKeyboardBuilder()

    for city in standard_cities:
        # Если город уже в списке выбранных, добавляем эмодзи галочки
        is_selected = city in selected_cities
        text = f"✅ {city}" if is_selected else city

        builder.button(text=text, callback_data=f"city_{city}")

    builder.adjust(2)  # Сетка по 2 кнопки в ряд

    # Дополнительные кнопки управления
    builder.row(InlineKeyboardButton(text="Свой вариант 📝", callback_data="city_own"))
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_params"),
        InlineKeyboardButton(text="Готово ✅", callback_data="done_cities")
    )

    return builder.as_markup()