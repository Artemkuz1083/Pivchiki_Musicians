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

    @classmethod
    def list_values(cls):
        """Возвращает список всех строковых значений инструментов."""
        return [member.value for member in cls]
