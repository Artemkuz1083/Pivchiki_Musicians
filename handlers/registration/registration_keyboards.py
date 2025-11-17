from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.enums.genres import Genre
from handlers.enums.instruments import Instruments

# клавиатура для инструментов
def make_keyboard_for_instruments(selected):
    standard_instruments = Instruments.list_values() + ["Свой вариант"]

    buttons = []
    for inst in standard_instruments:
        text = f"✅ {inst}" if inst in selected else inst
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"inst_{inst}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

    buttons = []
    for genre in genres:
        text = f"✅ {genre}" if genre in selected else genre
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"genre_{genre}")])
    buttons.append([InlineKeyboardButton(text="Готово ✅", callback_data="done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)