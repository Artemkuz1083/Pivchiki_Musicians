from typing import Dict

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


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
    """Создает клавиатуру меню фильтров с текущими установленными значениями."""

    # Получение текущих значений для отображения
    city = current_filters.get('city', 'Все')
    genres_count = len(current_filters.get('genres', []))
    level = current_filters.get('level', 'Все')

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text=f"Город: {city}",
        callback_data="set_filter_city"
    ))
    builder.row(types.InlineKeyboardButton(
        text=f"Жанры: {genres_count} выбрано",
        callback_data="set_filter_genres"
    ))
    builder.row(types.InlineKeyboardButton(
        text=f"Уровень: {level}",
        callback_data="set_filter_level"
    ))

    builder.row(types.InlineKeyboardButton(
        text="Сбросить все 🧹",
        callback_data="reset_filters"
    ))
    builder.row(types.InlineKeyboardButton(
        text="Назад к просмотру ➡️",
        callback_data="back_from_filters"
    ))

    return builder.as_markup()