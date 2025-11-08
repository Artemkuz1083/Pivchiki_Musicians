from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from .enums import PerformanceExperience
from .models import User
from .session import AsyncSessionLocal

async def check_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none() is not None


async def get_user(user_id: int) -> User | None:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.instruments))
            .options(selectinload(User.genres))
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