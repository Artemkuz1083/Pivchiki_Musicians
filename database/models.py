from sqlalchemy import (
    BigInteger, Integer, String, ForeignKey, Table, Column, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
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
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    theoretical_knowledge_level: Mapped[int] = mapped_column(Integer, nullable=False)
    has_performance_experience: Mapped[PerformanceExperience] = mapped_column(
        SQLEnum(PerformanceExperience), nullable=False
    )

    genres: Mapped[List[str]] = relationship(
        secondary=user_genre,
        collection_class=list,
        viewonly=False
    )

    instruments: Mapped[List["Instrument"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    proficiency_level: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="instruments")