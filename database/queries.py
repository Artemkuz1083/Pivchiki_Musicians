from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .enums import PerformanceExperience
from .models import User, Instrument
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
        user = result.scalar_one_or_none()
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
    """Обновляет уровень владения (proficiency_level) для конкретного инструмента по его ID."""
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
    """Обновляет опыт выступлений (и его описание)."""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(has_performance_experience=experience_type)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_theory_level(user_id: int, theory_level: int) -> None:
    """
    Обновляет поле theoretical_knowledge_level для пользователя по его ID.
    """
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
    """Обновляет одно аудио/ГС (старое строковое поле)."""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(audio_path=file_id)
        )
        await session.execute(stmt)
        await session.commit()

async def save_user_link(user_id: int, url: str) -> None:
    """Обновляет одну внешнюю ссылку (старое строковое поле)."""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(external_link=url)
        )
        await session.execute(stmt)
        await session.commit()

async def save_user_profile_photo(user_id: int, file_id: str) -> None:
    """Обновляет одно фото профиля (старое строковое поле)."""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(photo_path=file_id)
        )
        await session.execute(stmt)
        await session.commit()

async def update_user_name(user_id: int, name: str) -> None:
    """Обновляет имя пользователя"""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(name=name)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_city(user_id: int, city: str) -> None:
    """Обновляет город"""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(city=city)
        )
        await session.execute(stmt)
        await session.commit()

async def update_user_instruments(user_id: int, instruments: List[Instrument]):
    """Обновляет список инструментов пользователя"""
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
    """Создает пользователя"""
    async with AsyncSessionLocal() as session:
        existing_user = await session.get(User, user_id)
        if existing_user:
            return existing_user
        user = User(id=user_id)
        session.add(user)
        await session.commit()

async def update_user_genres(user_id, genres: List[str]):
    """Обновляет список жанров"""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(genres=genres)
        )
        await session.execute(stmt)
        await session.commit()


async def update_user_instruments(user_id: int, instrument_names: list):
    """
    Обновляет инструменты, создавая и закрывая сессию внутри себя
    """
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