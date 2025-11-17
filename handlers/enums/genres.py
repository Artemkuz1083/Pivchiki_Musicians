from enum import Enum

class Genre(str, Enum):
    """
    Стандартные музыкальные жанры, доступные для выбора. FUCKIN GENRES!!1!
    """
    ROCK = "Рок"
    POP_ROCK = "Поп рок"
    GRUNGE = "Гранж"
    METAL = "Метал"
    NU_METAL = "Ню метал"
    PUNK = "Панк"

    # возвращаем список жанров
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]