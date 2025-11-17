from enum import Enum

class City(str, Enum):
    """
    Челябинск и близлежащие к нему города
    """
    CHELYABINSK = "Челябинск"
    KOPEYSK = "Копейск"
    MIASS = "Миасс"
    CHEBARKUL = "Чебаркуль"
    SATKA = "Сатка"
    ZLATOUST = "Златоуст"
    MAGNITOGORSK = "Магнитогорск"

    # возвращаем список городов
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]