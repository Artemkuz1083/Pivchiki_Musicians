from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.enums.genres import Genre
from handlers.enums.cities import City
from handlers.enums.instruments import Instruments

# клавиатура для инструментов
def make_keyboard_for_instruments(selected):
    standard_instruments = Instruments.list_values() + ["Свой вариант"]

    markup = InlineKeyboardBuilder()
    for inst in standard_instruments:
        text = f"✅ {inst}" if inst in selected else inst
        markup.add(InlineKeyboardButton(text=text, callback_data=f"inst_{inst}"))
    markup.add(InlineKeyboardButton(text="Готово ✅", callback_data="done"))

    markup.adjust(2, 2, 2, 1, 1)

    return markup.as_markup()

# клавиатура для оценивания практических умений
def keyboard_rating_practice(inst_id: int):
    markup = InlineKeyboardBuilder()

    for i in range(1, 6):
        stars =f"{i} ⭐️"
        button = InlineKeyboardButton(
            text=stars,
            callback_data=f"practice_{i}_{inst_id}"
        )
        markup.add(button)

    markup.adjust(5)

    return markup

# клавиатура со списком инструментов пользователя
def get_instrument_rating(instruments: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for instrument in instruments:
        builder.row(InlineKeyboardButton(
            text=f"{instrument.name} (ур. {instrument.proficiency_level})",
            callback_data=f"select_inst:{instrument.id}"
        ))

    builder.row(InlineKeyboardButton(text="Готово", callback_data="done_rating"))
    return builder.as_markup()

# клавиатура для жанров
def make_keyboard_for_genre(selected):
    genres = Genre.list_values()  + ["Свой вариант"]

    markup = InlineKeyboardBuilder()
    for genre in genres:
        text = f"✅ {genre}" if genre in selected else genre
        markup.add(InlineKeyboardButton(text=text, callback_data=f"genre_{genre}"))
    markup.add(InlineKeyboardButton(text="Готово ✅", callback_data="done"))

    markup.adjust(2, 2, 2, 1, 1)

    return markup.as_markup()

# клавиатура для выбора города
def make_keyboard_for_city():
    cities = City.list_values() + ["Свой вариант"]

    markup = InlineKeyboardBuilder()
    for city in cities:
        markup.add(InlineKeyboardButton(text=city, callback_data=f"city_{city}"))

    markup.adjust(2, 2, 2, 2, 1)

    return markup.as_markup()

# клавиатура для подтверждения города
def done_keyboard_for_city():
    markup = InlineKeyboardBuilder()

    by_text = types.InlineKeyboardButton(
        text="Верно",
        callback_data="right")
    by_audio = types.InlineKeyboardButton(
        text="Исправить",
        callback_data="wrong"
    )
    markup.add(by_text, by_audio)
    markup.adjust(2)
    return markup.as_markup()