from typing import Dict, Any, Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton, types

def format_band_profile(group_data: Dict[str, Any], success_message: Optional[str] = None) -> str:
    """Форматирует данные группы в виде текста анкеты."""

    name = group_data.get("name", "Не указано")
    year = group_data.get("foundation_year", "Не указан")
    genres = ", ".join(group_data.get("genres", [])) or "Не указаны"

    header = f"{success_message}\n\n" if success_message else ""

    profile_text = (
        f"{header} **АНКЕТА ГРУППЫ** \n"
        f"***\n"
        f" **{name.upper()}** \n"  
        f"***\n\n"
        f"**Год основания:** {year}\n"
        f"**Жанры:** {genres}\n"
        "\n***\n\n"
        "Выберите, что хотите изменить:"
    )

    return profile_text


def get_band_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора параметров группы, которые можно редактировать."""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Название", callback_data="edit_group_name"))
    builder.add(InlineKeyboardButton(text="Год основания", callback_data="edit_group_year"))
    builder.add(InlineKeyboardButton(text="Жанры", callback_data="edit_group_genres"))

    builder.adjust(3)
    return builder.as_markup()


async def send_band_profile(
        callback_or_message: types.CallbackQuery | types.Message,
        user_id: int,
        success_message: Optional[str] = None
):
    """Отправляет или редактирует сообщение с анкетой Бэнда и меню редактирования."""
    # Вам нужно реализовать эту функцию, которая возвращает Dict[str, Any]
    band_data = await get_band_data_by_user_id(user_id)

    # Отправка сообщения об успехе (если есть)
    if success_message:
        if isinstance(callback_or_message, types.CallbackQuery):
            # Используем callback.answer() для всплывающего уведомления ИЛИ message.answer()
            await callback_or_message.message.answer(success_message, parse_mode='Markdown')
        else:
            await callback_or_message.answer(success_message, parse_mode='Markdown')

    #Отправка самой анкеты с клавиатурой
    text = format_band_profile(band_data)
    markup = get_band_selection_keyboard()

    if isinstance(callback_or_message, types.CallbackQuery):
        # Отправляем новое сообщение, так как предыдущее было только текстом успеха
        await callback_or_message.message.answer(
            text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        await callback_or_message.answer(
            text,
            reply_markup=markup,
            parse_mode='Markdown'
        )