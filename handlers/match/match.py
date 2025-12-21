import logging

from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.models import User
from database.queries import get_my_matches, get_user

logger = logging.getLogger(__name__)
router = Router()


from aiogram.utils.keyboard import InlineKeyboardBuilder

PAGE_SIZE = 5

class MatchesCB(CallbackData, prefix="match"):
    action: str          # open | next | prev
    user_id: int | None  # id мэтча
    page: int

def matches_keyboard(matches: list[User], page: int):
    kb = InlineKeyboardBuilder()

    for user in matches:
        kb.button(
            text=f"{user.name} 🎵",
            callback_data=MatchesCB(
                action="open",
                user_id=user.id,
                page=page
            ).pack()
        )

    kb.adjust(1)

    nav = InlineKeyboardBuilder()

    if page > 0:
        nav.button(
            text="⬅️",
            callback_data=MatchesCB(
                action="prev",
                user_id=None,
                page=page - 1
            ).pack()
        )

    if len(matches) == PAGE_SIZE:
        nav.button(
            text="➡️",
            callback_data=MatchesCB(
                action="next",
                user_id=None,
                page=page + 1
            ).pack()
        )

    if nav.buttons:
        kb.row(*nav.buttons)

    return kb.as_markup()

@router.message(F.text == "👥 Мои мэтчи")
async def show_matches(message: types.Message):
    user_id = message.from_user.id
    page = 0

    matches = await get_my_matches(
        my_user_id=user_id,
        limit=PAGE_SIZE,
        offset=page * PAGE_SIZE
    )

    if not matches:
        return await message.answer("😔 У вас пока нет мэтчей")

    await message.answer(
        text="❤️ <b>Ваши мэтчи</b>",
        reply_markup=matches_keyboard(matches, page)
    )

@router.callback_query(MatchesCB.filter())
async def matches_callback(
    callback: types.CallbackQuery,
    callback_data: MatchesCB
):
    user_id = callback.from_user.id
    page = callback_data.page

    if callback_data.action in ("next", "prev"):
        matches = await get_my_matches(
            my_user_id=user_id,
            limit=PAGE_SIZE,
            offset=page * PAGE_SIZE
        )

        await callback.message.edit_reply_markup(
            reply_markup=matches_keyboard(matches, page)
        )
        await callback.answer()
        return

    if callback_data.action == "open":
        match_id = callback_data.user_id

        user = await (get_user(match_id))

        await render_profile(callback.message, user)


def rating_to_stars(level: int | None) -> str:
    return "⭐️" * (level or 0)

async def render_profile(message: types.Message, user: User):
    user_id = message.from_user.id
    logger.info("Загружаем анкету для пользователя ID=%s", user_id)


    if not user:
        await message.answer(
            "🏁 <b>Анкеты закончились!</b>",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    genres = ", ".join(g.name for g in user.genres) if user.genres else "Не указано"

    instruments = (
        "\n".join(
            f"• <b>{i.name}</b>: {rating_to_stars(i.proficiency_level)}"
            for i in user.instruments
        )
        if user.instruments else "Не указаны"
    )

    profile_text = (
        f"👤 <b>Имя:</b> {user.name or 'Не указано'}\n"
        f"🎂 <b>Возраст:</b> {user.age or 'Не указано'}\n"
        f"🏙 <b>Город:</b> {user.city or 'Не указано'}\n\n"
        f"📝 <b>О себе:</b>\n<i>{user.about_me or 'Не указано'}</i>\n\n"
        f"🧠 <b>Теория:</b> {rating_to_stars(user.theoretical_knowledge_level)}\n"
        f"🎤 <b>Опыт выступлений:</b> {getattr(user.has_performance_experience, 'value', 'Не указано')}\n\n"
        f"📞 <b>Контакты:</b> {user.contacts or 'Не указано'}\n"
        f"🔗 <b>Ссылка:</b> {user.external_link or 'Не указана'}\n\n"
        f"🎼 <b>Жанры:</b> {genres}\n\n"
        f"🎹 <b>Инструменты:</b>\n{instruments}"
    )

    if user.photo_path:
        await message.answer_photo(user.photo_path)

    if user.audio_path:
        await message.answer_audio(user.audio_path)

    await message.answer(profile_text, reply_markup=keyboard())

def keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Вернуться на главную"),
    )
    return kb.as_markup(resize_keyboard=True)