from enum import Enum

class Instruments(str, Enum):
    """
    Стандартные музыкальные инструменты.
    """
    GUITAR = "Гитара"
    DRUMS = "Барабаны"
    SYNTHESIZER = "Синтезатор"
    VOCAL = "Вокал"
    BASS = "Бас"
    VIOLIN = "Скрипка"

    # возвращаем список инструментов
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]
