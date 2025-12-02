import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

from sqlalchemy import select, update, delete, insert, func, exists
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .enums import PerformanceExperience, Actions
from .models import User, Instrument, GroupMember, GroupProfile, UserGenre, GroupGenre, UserLikesUser, UserLikesGroup
from .session import AsyncSessionLocal

async def check_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.unique().scalar_one_or_none() is not None

async def get_user(user_id: int) -> User | None:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.instruments))
        )
        result = await session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        return user


async def update_user(user_id: int, **kwargs) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        await session.execute(stmt)
        await session.commit()


async def update_instrument_level(instrument_id: int, new_level: int) -> None:
    from .models import Instrument

    async with AsyncSessionLocal() as session:
        stmt = (
            update(Instrument)
            .where(Instrument.id == instrument_id)
            .values(proficiency_level=new_level)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_experience(
        user_id: int,
        experience_type: PerformanceExperience) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(has_performance_experience=experience_type)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_theory_level(user_id: int, theory_level: int) -> None:
    async with AsyncSessionLocal() as session:
        # Формируем запрос на обновление
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(theoretical_knowledge_level=theory_level)
        )
        await session.execute(stmt)
        await session.commit()

async def save_user_audio(user_id: int, file_id: str) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(audio_path=file_id)
        )
        await session.execute(stmt)
        await session.commit()

async def save_user_link(user_id: int, url: str) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(external_link=url)
        )
        await session.execute(stmt)
        await session.commit()

async def save_user_profile_photo(user_id: int, file_id: str) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(photo_path=file_id)
        )
        await session.execute(stmt)
        await session.commit()

async def update_user_name(user_id: int, name: str) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(name=name)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_city(user_id: int, city: str) -> None:
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(city=city)
        )
        await session.execute(stmt)
        await session.commit()

async def update_user_instruments(user_id: int, instruments: List[Instrument]):
    async with AsyncSessionLocal() as session:
        # Получаем пользователя
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Обновляем relationship
        user.instruments = instruments  # Это заменяет текущие инструменты

        session.add(user)
        await session.commit()

async def create_user(user_id: int):
    async with AsyncSessionLocal() as session:
        existing_user = await session.get(User, user_id)
        if existing_user:
            return existing_user
        user = User(id=user_id)
        session.add(user)
        await session.commit()

async def update_user_genres(user_id, genres_names: List[str]):
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(UserGenre).where(UserGenre.user_id == user_id)
        )

        new_genres = [
            UserGenre(user_id=user_id, name=name) for name in genres_names
        ]

        session.add_all(new_genres)
        await session.commit()


async def update_user_instruments(user_id: int, instrument_names: list):
    async with AsyncSessionLocal() as session:
        # 1. Загружаем пользователя, используя сессию
        user_stmt = select(User).where(User.id == user_id).options(selectinload(User.instruments))
        user = (await session.execute(user_stmt)).scalar_one_or_none()

        current_levels = {inst.name: inst.proficiency_level for inst in user.instruments}

        # Удаляем старые записи
        await session.execute(delete(Instrument).where(Instrument.user_id == user_id))

        new_instrument_objects = []
        DEFAULT_PROFICIENCY_LEVEL = 1

        for name in instrument_names:
            level_to_assign = current_levels.get(name, DEFAULT_PROFICIENCY_LEVEL)
            new_instrument = Instrument(
                user_id=user_id,
                name=name,
                proficiency_level=level_to_assign
            )
            new_instrument_objects.append(new_instrument)

        user.instruments = new_instrument_objects
        await session.commit()

async def update_user_instruments_for_registration(user_id: int, instruments: List[Instrument]):
    async with AsyncSessionLocal() as session:
        # Получаем пользователя
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Обновляем relationship
        user.instruments = instruments  # Это заменяет текущие инструменты

        session.add(user)
        await session.commit()


async def update_user_about_me(user_id: int, about_me_text: str):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            user.about_me = about_me_text
            await session.commit()


async def create_group(group_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новую запись GroupProfile и добавляет пользователя как первого участника.
    """
    genres_to_save: List[str] = group_data.get("genres", [])
    user_id: int = group_data["user_id"]

    group_profile_data = {
        "name": group_data.get("name"),
        "formation_date": int(group_data.get("foundation_year")) if group_data.get("foundation_year") else None,
        "city": group_data.get("city"),
        "description": group_data.get("description"),
        "seriousness_level": group_data.get("seriousness_level"),
    }

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Создание профиля группы
                stmt = insert(GroupProfile).values(**group_profile_data).returning(GroupProfile.id)
                result = await session.execute(stmt)
                group_id = result.scalar_one()

                if genres_to_save:
                    new_genres = [
                        GroupGenre(group_id=group_id, name=name) for name in genres_to_save
                    ]
                    session.add_all(new_genres)

                # Добавление пользователя как основателя
                member_data = {
                    "group_id": group_id,
                    "user_id": group_data["user_id"],
                    "role": "Основатель"
                }
                await session.execute(insert(GroupMember).values(**member_data))

            return group_id
    except Exception as e:
        logging.error(f"Ошибка при создании группы. Данные: {group_data}. Ошибка: {e}", exc_info=True)
        return None


async def _get_group_id_by_user(user_id: int, session: AsyncSession) -> Optional[int]:
    """Возвращает ID группы (group_id), связанного с данным пользователем."""
    stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def update_band_year(user_id: int, new_year: str):
    """Обновляет год основания (formation_date: Integer) группы"""

    new_year_int = int(new_year)
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id:
            return

        stmt = (
            update(GroupProfile)
            .where(GroupProfile.id == group_id)
            .values(formation_date=new_year_int)
        )
        await session.execute(stmt)
        await session.commit()

async def update_band_name(user_id: int, new_name: str):
    """Обновляет название группы."""
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id:
            return

        stmt = (
            update(GroupProfile)
            .where(GroupProfile.id == group_id)
            .values(name=new_name)
        )
        await session.execute(stmt)
        await session.commit()


async def update_band_genres(user_id: int, genre_names: List[str]):
    """Обновляет список жанров группы."""
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id:
            return

        await session.execute(
            delete(GroupGenre).where(GroupGenre.group_id == group_id)
        )

        new_genres = [
            GroupGenre(group_id=group_id, name=name) for name in genre_names
        ]

        session.add_all(new_genres)
        await session.commit()

async def check_exist_band(user_id: int) -> bool:
    """Проверяет наличие группы"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == user_id))
        return result.unique().scalar_one_or_none() is not None


async def get_band_data_by_user_id(user_id: int) -> Dict[str, Any]:
    """
    Получает полный профиль группы по ID пользователя.
    """
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)

        if not group_id:
            return {
                "name": "Группа не зарегистрирована",
                "foundation_year": "Нет",
                "city": "Не указан",
                "description": "Не указано",
                "seriousness_level": "Не указан",
                "external_link": "Нет"
            }

        stmt = select(GroupProfile).where(GroupProfile.id == group_id)
        result = await session.execute(stmt)
        band_profile = result.unique().scalar_one_or_none()

    if not band_profile:
        return {}

    genres_stmt = select(GroupGenre.name).where(GroupGenre.group_id == group_id)
    genres_result = await session.execute(genres_stmt)
    band_genres = genres_result.scalars().all()

    level_display = "Не указан"
    if band_profile.seriousness_level:
        if hasattr(band_profile.seriousness_level, 'value'):
            level_display = band_profile.seriousness_level.value
        else:
            level_display = str(band_profile.seriousness_level)

    band_data = {
        "id": band_profile.id,
        "name": band_profile.name,
        "genres": band_genres,
        "foundation_year": str(band_profile.formation_date) if band_profile.formation_date else "Не указан",
        "external_link": None,
        "city": band_profile.city if band_profile.city else "Не указан",
        "description": band_profile.description if band_profile.description else "Не указано",
        "seriousness_level": level_display
    }

    return band_data

async def update_band_city(user_id: int, new_city: str) -> bool:
    """Обновляет город группы."""
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id: return False

        stmt = update(GroupProfile).where(GroupProfile.id == group_id).values(city=new_city)
        await session.execute(stmt)
        await session.commit()
        return True

async def update_band_description(user_id: int, new_description: str | None) -> bool:
    """Обновляет описание группы."""
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id: return False

        stmt = update(GroupProfile).where(GroupProfile.id == group_id).values(description=new_description)
        await session.execute(stmt)
        await session.commit()
        return True

async def update_band_seriousness_level(user_id: int, new_level: str) -> bool:
    """Обновляет уровень серьезности группы."""
    async with AsyncSessionLocal() as session:
        group_id = await _get_group_id_by_user(user_id, session)
        if not group_id: return False

        stmt = update(GroupProfile).where(GroupProfile.id == group_id).values(seriousness_level=new_level)
        await session.execute(stmt)
        await session.commit()
        return True

async def get_random_profile() -> User | None:
    """Получает рандомный профиль, исключая текущего пользователя"""
    async with AsyncSessionLocal() as session:

        stmt = (
            select(User)
            .order_by(func.random())
            .limit(1)
        )

        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

async def get_random_group() -> GroupProfile | None:
    """Получает рандомную группу, исключая текущую группу пользователя, если такая есть"""
    async with AsyncSessionLocal() as session:
        stmt = select(GroupProfile)

        stmt = stmt.order_by(func.random()).limit(1)

        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

async def save_user_interaction(swiper_id: int, target_id: int, action: Actions) -> None:
    """Сохраняет действие пользователя swiper_id на анкету target_id."""
    async with AsyncSessionLocal() as session:
        stmt = insert(UserLikesUser).values(
            swiper_user_id=swiper_id,
            target_user_id=target_id,
            action=action.value,  # Сохраняем строковое значение Enum
            created_at=datetime.now(timezone.utc)
        )
        await session.execute(stmt)
        await session.commit()

async def save_group_interaction(swiper_id: int, target_group_id: int, action: Actions) -> None:
    """Сохраняет действие пользователя swiper_id на группу target_group_id."""
    async with AsyncSessionLocal() as session:
        stmt = insert(UserLikesGroup).values(
            swiper_user_id=swiper_id,
            target_group_id=target_group_id,
            action=action.value,
            created_at=datetime.now(timezone.utc)
        )
        await session.execute(stmt)
        await session.commit()


async def get_profile_which_not_action(swiper_id: int):
    """Выводит нового пользователя исключая тех кого видел наш пользователь"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .where(User.id != swiper_id)
            .where(User.is_visible)
            .where(
                ~exists().where(
                    (UserLikesUser.target_user_id == User.id) &
                    (UserLikesUser.swiper_user_id == swiper_id)
                )
            )
            .order_by(func.random())
            .limit(1)
        )

        result = await session.execute(stmt)
        user = result.scalars().first()
        return user


async def get_band_which_not_action(swiper_id: int):
    """Выводим группу, где пользователь не является участников"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(GroupProfile)
            .where(GroupProfile.is_visible)
            .where(
                ~exists().where(
                    (GroupMember.user_id == swiper_id) &
                    (GroupMember.group_id == GroupProfile.id)
                )
            )
            .where(
                ~exists().where(
                    (UserLikesGroup.target_group_id == GroupProfile.id) &
                    (UserLikesGroup.swiper_user_id == swiper_id)
                )
            )
            .order_by(func.random())
            .limit(1)
        )

        result = await session.execute(stmt)
        user = result.scalars().first()
        return user
