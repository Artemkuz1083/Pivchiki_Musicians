
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
def show_reply_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Следующая анкета")
    kb.button(text="Подробнее")
    kb.button(text="Вернуться на главную")

    kb.adjust(1)

    return kb.as_markup()