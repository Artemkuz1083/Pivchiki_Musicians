from sqlalchemy import (
    BigInteger, Integer, String, ForeignKey, Enum as SQLEnum, ARRAY, Text, JSON, DateTime, Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional, Dict
from datetime import datetime, timezone

from handlers.enums.seriousness_level import SeriousnessLevel
from .enums import PerformanceExperience, FinancialStatus, Actions

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    city: Mapped[str] = mapped_column(String, nullable=True)

    contacts: Mapped[str] = mapped_column(String, nullable=True)

    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    theoretical_knowledge_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    has_performance_experience: Mapped[Optional[PerformanceExperience]] = mapped_column(
        SQLEnum(PerformanceExperience), nullable=True
    )
    photo_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    audio_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    about_me: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    instruments: Mapped[List["Instrument"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    genres: Mapped[List["UserGenre"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    proficiency_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="instruments")

class UserGenre(Base):
    __tablename__ = "user_genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False) # Название жанра

    user: Mapped["User"] = relationship(back_populates="genres")

class GroupGenre(Base):
    __tablename__ = "group_genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("group_profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False) # Название жанра

    group: Mapped["GroupProfile"] = relationship(back_populates="genres")

class GroupProfile(Base):
    __tablename__ = "group_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=True)

    formation_date: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    platforms: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    seriousness_level: Mapped[Optional[SeriousnessLevel]] = mapped_column(
        SQLEnum(SeriousnessLevel, name='seriousness_level'), nullable=True
    )

    financial_status: Mapped[Optional[FinancialStatus]] = mapped_column(
        SQLEnum(FinancialStatus), nullable=True
    )
    concerts: Mapped[Optional[Dict[int, str]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    members: Mapped[List["GroupMember"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    genres: Mapped[List["GroupGenre"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("group_profiles.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    role: Mapped[str] = mapped_column(String, nullable=False)

    group: Mapped["GroupProfile"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class UserLikesUser(Base):
    __tablename__ = "user_likes_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Кто лайкнул
    swiper_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Кого лайкнули
    target_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    action: Mapped[Optional[Actions]] = mapped_column(
        SQLEnum(Actions), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    swiper: Mapped["User"] = relationship(foreign_keys=[swiper_user_id])
    target: Mapped["User"] = relationship(foreign_keys=[target_user_id])


class UserLikesGroup(Base):
    __tablename__ = "user_likes_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Кто лайкнул
    swiper_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Какую группу лайкнули
    target_group_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("group_profiles.id", ondelete="CASCADE"), nullable=False
    )

    action: Mapped[Optional[Actions]] = mapped_column(
        SQLEnum(Actions), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    swiper: Mapped["User"] = relationship(foreign_keys=[swiper_user_id])
    target_group: Mapped["GroupProfile"] = relationship(foreign_keys=[target_group_id])