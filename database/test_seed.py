import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import User, Instrument, GroupProfile, GroupMember, UserGenre, GroupGenre
from .enums import PerformanceExperience, FinancialStatus
from handlers.enums.cities import City
from handlers.enums.genres import Genre as GenreEnum
from handlers.enums.instruments import Instruments

# === Настройка данных ===
CITIES_ENUM = [c.value for c in City]
GENRES_ENUM = [g.value for g in GenreEnum]
INSTRUMENTS_ENUM = [i.value for i in Instruments]
PERF_EXP_VALUES = [e.value for e in PerformanceExperience]
FIN_STATUSES = [f.value for f in FinancialStatus]

CUSTOM_CITIES = ["Троицк", "Карабаш", "Верхний Уфалей", "Южноуральск", "Аша"]
CUSTOM_GENRES = ["Джаз", "Хип-хоп", "Электроника", "Фолк", "Панк", "Рэп"]
CUSTOM_INSTRUMENTS = ["Перкуссия", "Флейта", "Скрипка", "Аккордеон"]

ALL_CITIES = CITIES_ENUM + CUSTOM_CITIES
ALL_GENRES = GENRES_ENUM + CUSTOM_GENRES
ALL_INSTRUMENTS = INSTRUMENTS_ENUM + CUSTOM_INSTRUMENTS


def _random_choice_with_custom(enum_list, custom_list, custom_prob=0.3):
    return random.choice(custom_list) if random.random() < custom_prob else random.choice(enum_list)


# НОВАЯ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ для генерации контактов
def _generate_random_contacts(user_id: int) -> str | None:
    """Генерирует случайный контакт (Telegram или Email)."""
    if random.random() < 0.2:  # 20% пользователей без контактов
        return None

    if random.random() < 0.6:  # 60% шанс на Telegram
        return f"@{random.choice(['rock', 'jazz', 'band', 'user'])}musician_{user_id}"
    else:  # 40% шанс на Email
        return f"testuser_{user_id}@example.com"


async def seed_initial_data(session: AsyncSession):
    # Проверяем, есть ли уже пользователи — если да, не сидим
    result = await session.execute(select(User).limit(1))
    if result.unique().scalar_one_or_none():
        print("✅ База уже содержит данные. Сидирование пропущено.")
        return

    print("🌱 Создаём тестовые данные...")

    user_id_counter = 1
    group_id_counter = 1001

    # --- 2. 10 групп по 2–4 участника ---
    for _ in range(10):
        # Создаём основателя
        founder_city = random.choice(ALL_CITIES)
        founder_genre_names = random.sample(ALL_GENRES, k=random.randint(1, 2))

        # 🔥 ИЗМЕНЕНИЕ 1: Добавляем contacts
        founder_contacts = _generate_random_contacts(user_id_counter)

        founder = User(
            id=user_id_counter,
            city=founder_city,
            name=f"Founder_{user_id_counter}",
            age=random.randint(18, 45),
            theoretical_knowledge_level=random.randint(1, 5) if random.random() > 0.3 else None,
            has_performance_experience=random.choice(PERF_EXP_VALUES) if random.random() > 0.3 else None,
            about_me=f"Основатель группы из {founder_city}" if random.random() > 0.4 else None,
            contacts=founder_contacts,  # <-- ДОБАВЛЕНО
        )
        for genre_name in founder_genre_names:
            founder.genres.append(UserGenre(name=genre_name))
        session.add(founder)

        # Инструменты для основателя
        for _ in range(random.randint(1, 2)):
            instr = Instrument(
                user_id=user_id_counter,
                name=_random_choice_with_custom(INSTRUMENTS_ENUM, CUSTOM_INSTRUMENTS),
                proficiency_level=random.randint(1, 5)
            )
            session.add(instr)

        group_city = random.choice(ALL_CITIES)
        group_genre_names = random.sample(ALL_GENRES, k=random.randint(1, 3))
        group = GroupProfile(
            id=group_id_counter,
            name=f"Group_{group_id_counter}",
            city=group_city,
            formation_date=random.randint(2015, 2025) if random.random() > 0.3 else None,
            financial_status=random.choice(FIN_STATUSES) if random.random() > 0.4 else None,
            description=f"Группа из {group_city}" if random.random() > 0.5 else None,
            platforms=["VK", "YouTube"] if random.random() > 0.6 else ["Instagram"]
        )
        for genre_name in group_genre_names:
            group.genres.append(GroupGenre(name=genre_name))
        session.add(group)

        members = [founder]
        num_extra = random.randint(1, 3)

        # Создаём дополнительных участников
        for i in range(num_extra):
            member_id = user_id_counter + i + 1
            member_city = group_city
            member_genre_names = random.sample(group_genre_names, k=1)

            # 🔥 ИЗМЕНЕНИЕ 2: Добавляем contacts
            member_contacts = _generate_random_contacts(member_id)

            member = User(
                id=member_id,
                city=member_city,
                name=f"Member_{member_id}",
                age=random.randint(16, 60) if random.random() > 0.2 else None,
                theoretical_knowledge_level=random.randint(1, 5) if random.random() > 0.3 else None,
                has_performance_experience=random.choice(PERF_EXP_VALUES) if random.random() > 0.3 else None,
                about_me=f"Участник группы из {member_city}" if random.random() > 0.4 else None,
                contacts=member_contacts,  # <-- ДОБАВЛЕНО
            )
            for genre_name in member_genre_names:
                member.genres.append(UserGenre(name=genre_name))
            session.add(member)

            # 🔥 ОБЯЗАТЕЛЬНО: добавляем инструмент каждому участнику
            for _ in range(random.randint(1, 2)):
                instr = Instrument(
                    user_id=member_id,
                    name=_random_choice_with_custom(INSTRUMENTS_ENUM, CUSTOM_INSTRUMENTS),
                    proficiency_level=random.randint(1, 5)
                )
                session.add(instr)

            members.append(member)

        # Назначаем роли
        roles = ["Вокал", "Гитара", "Бас", "Барабаны", "Клавишник", "Менеджер"]
        for idx, member in enumerate(members):
            gm = GroupMember(
                group_id=group_id_counter,
                user_id=member.id,
                role=roles[idx % len(roles)]
            )
            session.add(gm)

        user_id_counter += num_extra + 1
        group_id_counter += 1

    await session.commit()
    print("✅ Тестовые данные успешно добавлены!")