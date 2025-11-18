from enum import Enum

class Instruments(str, Enum):
    """
    Стандартные музыкальные инструменты.
    """
    BASS = "Бас"
    RITM_GUITAR = "Ритм гитара"
    VOCAL = "Вокал"
    SOLO_GUITAR = "Соло гитара"
    SYNTHESIZER = "Синтезатор"
    DRUMS = "Барабаны"

    # возвращаем список инструментов
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]
