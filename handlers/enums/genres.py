from enum import Enum

class Genre(str, Enum):
    """
    Стандартные музыкальные жанры, доступные для выбора. FUCKIN GENRES!!1!
    """
    ROCK = "Рок"
    INDY = "Инди"
    METAL = "Метал"
    POP_ROCK = "Поп рок"
    GRUNGE = "Гранж"
    BLUZ = "Блюз"

    # возвращаем список жанров
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]