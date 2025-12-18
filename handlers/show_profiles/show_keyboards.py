from typing import Dict, List

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.enums import PerformanceExperience
from handlers.enums.cities import City
from handlers.enums.genres import Genre
from handlers.enums.instruments import Instruments
from handlers.enums.seriousness_level import SeriousnessLevel


# клавиатура для выбора, что хочет смотреть пользователь
def choose_keyboard_for_show():
    markup = InlineKeyboardBuilder()

    _bands = types.InlineKeyboardButton(
        text="Группы",
        callback_data="chs_bands")
    _artist = types.InlineKeyboardButton(
        text="Музыкантов",
        callback_data="chs_artist"
    )
    markup.adjust(2)
    markup.add(_bands, _artist)
    return markup.as_markup()

# клавиатура для управления в режиме просмотра анкет
def show_reply_keyboard_for_unregistered_users():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Следующая анкета")
    kb.button(text="Подробнее")
    kb.button(text="Вернуться на главную")

    kb.adjust(1)

    return kb.as_markup()

# клавиатура для управления в режиме просмотра анкет
def show_reply_keyboard_for_registered_users():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Следующая анкета"),
        types.KeyboardButton(text="❤️")
    )
    kb.row(
        types.KeyboardButton(text="Фильтр 🔍"),
        types.KeyboardButton(text="Вернуться на главную")
    )

    return kb.as_markup(resize_keyboard=True)


def get_filter_menu_keyboard(current_filters: Dict) -> types.InlineKeyboardMarkup:
    """
    Создает клавиатуру главного меню фильтров, отображая текущие выбранные параметры.
    """

    # 1. --- Получение текущих значений фильтров или значений по умолчанию ---

    # Города
    cities = current_filters.get('cities', [])
    city_display = f"{len(cities)} выбрано" if cities else "Все"

    # Жанры
    genres = current_filters.get('genres', [])
    genre_display = f"{len(genres)} выбрано" if genres else "Все"

    # Инструменты
    instruments = current_filters.get('instruments', [])
    instrument_display = f"{len(instruments)} выбрано" if instruments else "Все"

    # Возраст
    age_modes_map = {
        'peers': 'Ровесники',
        'younger': 'Младше',
        'older': 'Старше'
    }
    age_mode_key = current_filters.get('age_mode', 'all')
    age_filter_display = age_modes_map.get(age_mode_key, 'Все')

    # Уровень знаний
    level = current_filters.get('min_level', 'Все')

    # Опыт выступлений (НОВЫЙ)
    experience = current_filters.get('experience', [])
    experience_display = f"{len(experience)} выбрано" if experience else "Не важно"

    builder = InlineKeyboardBuilder()

    # 2. --- Добавление кнопок фильтров (по рядам) ---

    # Город
    builder.row(types.InlineKeyboardButton(
        text=f"🏙️ Города: {city_display}",
        callback_data="set_filter_city"
    ))

    # Жанры
    builder.row(types.InlineKeyboardButton(
        text=f"🎶 Жанры: {genre_display}",
        callback_data="set_filter_genres"
    ))

    # Инструменты
    builder.row(types.InlineKeyboardButton(
        text=f"🎸 Инструменты: {instrument_display}",
        callback_data="set_filter_instruments"
    ))

    # Опыт выступлений
    builder.row(types.InlineKeyboardButton(
        text=f"🎙️ Опыт выступлений: {experience_display}",
        callback_data="set_filter_experience"
    ))

    # Возраст
    builder.row(types.InlineKeyboardButton(
        text=f"🎂 Возраст: {age_filter_display}",
        callback_data="set_filter_age"
    ))

    # Уровень
    builder.row(types.InlineKeyboardButton(
        text=f"⭐ Уровень: {level}",
        callback_data="set_filter_level"
    ))

    # 3. --- Кнопки управления ---

    builder.row(
        types.InlineKeyboardButton(
            text="Сбросить фильтры 🗑️",
            callback_data="reset_all_filters"
        ),
        types.InlineKeyboardButton(
            # ИЗМЕНЕНИЕ: Название кнопки
            text="Смотреть анкеты 👀",
            # Callback остается прежним для упрощения логики завершения
            callback_data="exit_filters_menu"
        )
    )

    return builder.as_markup()


def make_instrument_filter_keyboard(selected_instruments: List[str]) -> InlineKeyboardMarkup:
    """Создает Inline-клавиатуру для выбора инструментов-фильтров."""
    builder = InlineKeyboardBuilder()

    # 1. Добавляем стандартные инструменты из Enum
    for instrument_value in Instruments.list_values():
        is_selected = instrument_value in selected_instruments
        text = f"✅ {instrument_value}" if is_selected else instrument_value

        # Используем префикс "filter_inst_"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"filter_inst_{instrument_value}"
        ))

    # Добавляем выбранные пользовательские инструменты (если они есть)
    for name in selected_instruments:
        # Проверяем, что это не стандартный Enum
        if name not in Instruments.list_values():
            text = f"✅ {name} (свой)"
            builder.add(InlineKeyboardButton(
                text=text,
                callback_data=f"filter_inst_{name}"
            ))

    # Устанавливаем отображение в 2 столбца
    builder.adjust(2)

    # 2. Добавляем кнопки управления в отдельные ряды
    builder.row(InlineKeyboardButton(
        text="Свой вариант 📝",
        callback_data="filter_inst_custom"
    ))

    builder.row(InlineKeyboardButton(
        text="Готово ✅",
        callback_data="done_filter_instruments"
    ))

    return builder.as_markup()


def make_city_filter_keyboard(selected_cities: List[str]) -> InlineKeyboardMarkup:
    """Создает Inline-клавиатуру для выбора городов-фильтров."""
    builder = InlineKeyboardBuilder()

    # 1. Добавляем стандартные города из Enum
    for city_value in City.list_values():
        is_selected = city_value in selected_cities
        text = f"✅ {city_value}" if is_selected else city_value

        # Используем префикс "filter_city_"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"filter_city_{city_value}"
        ))

    # Добавляем выбранные пользовательские города (если они были введены)
    for name in selected_cities:
        # Проверяем, что это не стандартный Enum
        if name not in City.list_values():
            text = f"✅ {name} (свой)"
            builder.add(InlineKeyboardButton(
                text=text,
                callback_data=f"filter_city_{name}"
            ))

    # Устанавливаем отображение в 2 столбца
    builder.adjust(2)

    # 2. Добавляем кнопки управления в отдельные ряды
    builder.row(InlineKeyboardButton(
        text="Свой вариант 📝",
        callback_data="filter_city_custom_prompt"
    ))

    builder.row(InlineKeyboardButton(
        text="Готово ✅",
        callback_data="done_filter_city"
    ))

    return builder.as_markup()


def make_genre_filter_keyboard(selected_genres: List[str]) -> InlineKeyboardMarkup:
    """Создает Inline-клавиатуру для выбора жанров-фильтров."""
    builder = InlineKeyboardBuilder()

    # 1. Добавляем стандартные жанры из Enum
    for genre_value in Genre.list_values():
        is_selected = genre_value in selected_genres
        text = f"✅ {genre_value}" if is_selected else genre_value

        # Используем префикс "filter_genre_"
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"filter_genre_{genre_value}"
        ))

    # Добавляем выбранные пользовательские жанры (если они были введены)
    for name in selected_genres:
        # Проверяем, что это не стандартный Enum
        if name not in Genre.list_values():
            text = f"✅ {name} (свой)"
            builder.add(InlineKeyboardButton(
                text=text,
                callback_data=f"filter_genre_{name}"
            ))

    # Устанавливаем отображение в 2 столбца
    builder.adjust(2)

    # 2. Добавляем кнопки управления
    builder.row(InlineKeyboardButton(
        text="Свой вариант 📝",
        callback_data="filter_genre_custom_prompt"
    ))

    builder.row(InlineKeyboardButton(
        text="Готово ✅",
        callback_data="done_filter_genres"
    ))

    return builder.as_markup()


def make_age_filter_keyboard(current_mode: str) -> types.InlineKeyboardMarkup:
    """Клавиатура для выбора режима фильтрации по возрасту."""
    builder = InlineKeyboardBuilder()

    modes = {
        'peers': 'Ровесники (± 2 года)',
        'younger': 'Младше',
        'older': 'Старше',
        'all': 'Любой возраст (Сбросить)'
    }

    for mode_key, mode_text in modes.items():
        text = f"✅ {mode_text}" if mode_key == current_mode else mode_text
        builder.row(types.InlineKeyboardButton(
            text=text,
            callback_data=f"age_mode_{mode_key}"
        ))

    builder.row(types.InlineKeyboardButton(
        text="Назад к фильтрам ⬅️",
        callback_data="back_from_age_filter"
    ))

    return builder.as_markup()

def make_experience_filter_keyboard(selected_experiences: List[str]) -> types.InlineKeyboardMarkup:
    """Создает Inline-клавиатуру для выбора опыта выступлений-фильтров."""
    builder = InlineKeyboardBuilder()

    # 1. Добавляем варианты опыта из Enum
    for exp_value in PerformanceExperience.list_values():
        is_selected = exp_value in selected_experiences
        text = f"✅ {exp_value}" if is_selected else exp_value

        # Используем префикс "filter_exp_"
        builder.row(types.InlineKeyboardButton(
            text=text,
            callback_data=f"filter_exp_{exp_value}"
        ))

    # 2. Кнопки управления
    builder.row(
        types.InlineKeyboardButton(
            text="Не важно / Сбросить 🗑️",
            callback_data="reset_filter_experience"
        ),
        types.InlineKeyboardButton(
            text="Готово ✅",
            callback_data="done_filter_experience"
        )
    )

    return builder.as_markup()


def make_level_filter_keyboard(current_level: int | None) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Создаем 5 кнопок уровней
    for i in range(1, 6):
        # Рисуем звездочки
        stars = "⭐️" * i
        text = f"{i} - {stars}"

        # Если этот уровень сейчас выбран, помечаем галочкой
        if current_level == i:
            text = f"✅ {text}"

        builder.row(types.InlineKeyboardButton(
            text=text,
            callback_data=f"level_val_{i}"
        ))

    # Кнопка сброса
    builder.row(types.InlineKeyboardButton(
        text="Не важно (Сбросить) 🗑️",
        callback_data="reset_filter_level"
    ))

    # Кнопка назад
    builder.row(types.InlineKeyboardButton(
        text="Назад ↩️",
        callback_data="back_from_level_filter"
    ))

    return builder.as_markup()


def get_group_filter_menu_keyboard(current_filters: Dict) -> types.InlineKeyboardMarkup:
    # 1. Получаем текущие настройки для городов и жанров
    cities = current_filters.get('cities', [])
    city_display = f"{len(cities)} выбрано" if cities else "Все"

    genres = current_filters.get('genres', [])
    genre_display = f"{len(genres)} выбрано" if genres else "Все"

    # --- ИСПРАВЛЕНИЕ ДЛЯ УРОВНЯ ---
    # Достаем список КОРОТКИХ имен (например, ['HOBBY', 'PRO'])
    selected_names = current_filters.get('seriousness_level_names', [])

    if not selected_names:
        level_display = "Любой"
    else:
        # Превращаем ['HOBBY'] в читаемое название для меню
        readable_names = []
        for name in selected_names:
            try:
                # Берем значение из Enum и убираем текст в скобках для краткости
                full_val = SeriousnessLevel[name.upper()].value
                short_val = full_val.split('(')[0].strip()
                readable_names.append(short_val)
            except (KeyError, ValueError):
                continue

        level_display = ", ".join(readable_names)

        # Если текст слишком длинный, показываем кол-во
        if len(level_display) > 20:
            level_display = f"Выбрано: {len(selected_names)}"
    # ------------------------------

    builder = InlineKeyboardBuilder()

    # 2. Кнопки настроек
    builder.row(types.InlineKeyboardButton(
        text=f"🏙️ Города: {city_display}",
        callback_data="set_group_filter_city"
    ))

    builder.row(types.InlineKeyboardButton(
        text=f"🎶 Жанры: {genre_display}",
        callback_data="set_group_filter_genres"
    ))

    builder.row(types.InlineKeyboardButton(
        text=f"📊 Уровень: {level_display}",
        callback_data="set_group_filter_level"
    ))

    # 3. Управление
    builder.row(
        types.InlineKeyboardButton(
            text="Сбросить фильтры 🗑️",
            callback_data="reset_group_filters"
        ),
        types.InlineKeyboardButton(
            text="Смотреть группы 👀",
            callback_data="exit_group_filters_menu"
        )
    )
    return builder.as_markup()


# Клавиатура выбора уровня серьезности (Hobby, Amateur, Pro...)
def make_seriousness_filter_keyboard(selected_names: List[str]) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for member in SeriousnessLevel:
        # member.name (например, "HOBBY") используется для логики и callback_data
        # member.value (например, "Хобби (редкие репетиции)") используется для текста кнопки

        is_selected = member.name in selected_names
        text = f"✅ {member.value}" if is_selected else member.value

        builder.row(types.InlineKeyboardButton(
            text=text,
            # НОВАЯ КОРОТКАЯ CALLBACK_DATA: "fgl_hobby", "fgl_pro" (максимум ~10-15 байт)
            callback_data=f"fgl_{member.name.lower()}"
        ))

    builder.row(types.InlineKeyboardButton(
        text="Готово ✅",
        callback_data="done_group_filter_level"
    ))
    return builder.as_markup()