from sqlalchemy import (
    BigInteger, Integer, String, ForeignKey, Table, Column, Enum as SQLEnum, ARRAY, Text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional
from .enums import PerformanceExperience

class Base(DeclarativeBase):
    pass


user_genre = Table(
    "user_genre",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("genre", String, primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    city: Mapped[str] = mapped_column(String, nullable=True)

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

    instruments: Mapped[List["Instrument"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    genres: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    proficiency_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="instruments")