import html
from typing import Dict, Any, Optional

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.queries import get_band_data_by_user_id


def format_band_profile(group_data: Dict[str, Any], success_message: Optional[str] = None) -> str:
    """Форматирует данные группы в виде красивого HTML-текста."""

    # Получаем и экранируем данные, чтобы не сломать HTML
    name = html.escape(group_data.get("name", "Не указано"))
    year = group_data.get("foundation_year", "Не указан")

    city = html.escape(group_data.get("city", "Не указан"))
    description = html.escape(group_data.get("description", "Не указано"))
    level = group_data.get("seriousness_level", "Не указан")

    # Форматирование жанров
    genres_list = group_data.get("genres", [])
    if genres_list:
        # Красиво отображаем жанры (можно добавить #)
        genres = ", ".join([html.escape(g) for g in genres_list])
    else:
        genres = "Не указаны"

    # Формируем заголовок (сообщение об успехе)
    header = f"✅ <b>{success_message}</b>\n\n" if success_message else ""

    profile_text = (
        f"{header}"
        f"🎸 <b>ПРОФИЛЬ ГРУППЫ</b>\n"
        f"\n"
        f"🏷 <b>Название:</b> {name}\n"
        f"📅 <b>Год основания:</b> {year}\n"
        f"🏙 <b>Город:</b> {city}\n"
        f"📊 <b>Уровень:</b> {level}\n"
        f"🎶 <b>Жанры:</b> <i>{genres}</i>\n"
        f"\n"
        f"📝 <b>О себе:</b>\n"
        f"<i>{description}</i>\n"
        f"\n"
        "👇 <b>Выберите, что хотите изменить:</b>"
    )

    return profile_text


def get_band_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора параметров группы с эмодзи."""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🏷 Название", callback_data="edit_band_name"))
    builder.add(InlineKeyboardButton(text="📅 Год основания", callback_data="edit_band_year"))

    builder.add(InlineKeyboardButton(text="🏙 Город", callback_data="edit_band_city"))
    builder.add(InlineKeyboardButton(text="🎶 Жанры", callback_data="edit_band_genres"))

    builder.add(InlineKeyboardButton(text="📝 О себе", callback_data="edit_band_description"))
    builder.add(InlineKeyboardButton(text="📊 Уровень", callback_data="edit_band_level"))

    builder.adjust(2, 2, 2)
    return builder.as_markup()


async def send_band_profile(
        callback_or_message: types.CallbackQuery | types.Message,
        user_id: int,
        success_message: Optional[str] = None
):
    """Отправляет или редактирует сообщение с анкетой группы и меню редактирования."""

    # Получаем данные (предполагается, что get_band_data_by_user_id возвращает dict или None)
    band_data = await get_band_data_by_user_id(user_id)

    if not band_data:
        # Обработка случая, если группа не найдена
        error_text = "⚠️ <b>Группа не найдена.</b> Попробуйте зарегистрировать её заново."
        if isinstance(callback_or_message, types.CallbackQuery):
            await callback_or_message.message.answer(error_text, parse_mode='HTML')
        else:
            await callback_or_message.answer(error_text, parse_mode='HTML')
        return

    # Если есть сообщение об успехе, отправляем его отдельным уведомлением (опционально)
    # Но в format_band_profile мы его тоже добавляем в текст, так что тут можно просто отправить, если нужно
    # В оригинале вы отправляли отдельным сообщением. Оставим логику, но с HTML.
    if success_message:
        if isinstance(callback_or_message, types.CallbackQuery):
            await callback_or_message.message.answer(f"{success_message}", parse_mode='HTML')
        else:
            await callback_or_message.answer(f"{success_message}", parse_mode='HTML')

    # Формируем текст анкеты.
    # Примечание: success_message можно не передавать внутрь format_band_profile,
    # если мы уже отправили его выше отдельным сообщением, чтобы не дублировать.
    # Но для красивого обновления "на лету" (без спама сообщениями) лучше включать его в текст.
    # Здесь оставим как в оригинале (отдельное сообщение + текст профиля).

    text = format_band_profile(band_data, success_message=None)
    markup = get_band_selection_keyboard()

    if isinstance(callback_or_message, types.CallbackQuery):
        # Отправляем новое сообщение с анкетой
        await callback_or_message.message.answer(
            text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    else:
        await callback_or_message.answer(
            text,
            reply_markup=markup,
            parse_mode='HTML'
        )