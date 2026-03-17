import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.enums import Actions
from database.queries import get_users_who_liked_me, save_user_interaction, track_event
from handlers.start import start
from states.states_likes import LikesStates
# from utils.analytics import track_event

logger = logging.getLogger(__name__)
router = Router()


def rating_to_stars(level: int | None) -> str:
    return "⭐️" * (level or 0)


def keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Следующая анкета"),
        types.KeyboardButton(text="❤️ Оценить анкету"),
    )
    kb.row(
        types.KeyboardButton(text="Вернуться на главную"),
    )
    return kb.as_markup(resize_keyboard=True)


async def render_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await track_event(user_id, "profile_card_shown", {"target_id": user_id})
    logger.info("Загружаем анкету для пользователя ID=%s", user_id)

    user = await get_users_who_liked_me(my_user_id=user_id)

    if not user:
        await message.answer(
            "🏁 <b>Анкеты закончились!</b>",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await state.update_data(current_target_id=user.id)

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


@router.message(F.text.startswith("❤️ Лайки"))
async def show_likes(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await track_event(user_id, "likes_view_started")
    logger.info("Пользователь ID=%s вошёл в режим лайков", message.from_user.id)
    await state.set_state(LikesStates.see_profiles)
    await render_profile(message, state)


@router.message(F.text == "Следующая анкета", LikesStates.see_profiles)
async def skip_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("current_target_id")
    await track_event(message.from_user.id, "profile_interaction", {"action": "skip"})
    logger.info(
        "Пользователь ID=%s SKIP ID=%s",
        message.from_user.id,
        target_id
    )

    if not target_id:
        await message.answer("⚠️ Анкета не найдена")
        return

    try:
        logger.info("Делаем запрос в бд")
        await save_user_interaction(
            message.from_user.id,
            target_id,
            Actions.SKIP
        )
    except Exception as e:
        print("save error, e")


    await render_profile(message, state)


@router.message(F.text == "❤️ Оценить анкету", LikesStates.see_profiles)
async def like_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("current_target_id")

    if not target_id:
        await message.answer("⚠️ Анкета не найдена")
        return

    await save_user_interaction(
        message.from_user.id,
        target_id,
        Actions.LIKE
    )
    await track_event(message.from_user.id, "profile_interaction", {"action": "like"})
    logger.info(
        "Пользователь ID=%s LIKE ID=%s",
        message.from_user.id,
        target_id
    )

    await message.answer("💖 Вы оценили анкету")
    await render_profile(message, state)


@router.message(F.text == "Вернуться на главную", LikesStates.see_profiles)
async def back_to_main(message: types.Message, state: FSMContext):
    logger.info("Пользователь ID=%s вышел из лайков", message.from_user.id)
    await state.clear()
    await start(message, state)
