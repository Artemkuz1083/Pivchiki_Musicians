from enum import Enum


class SeriousnessLevel(str, Enum):
    """
    Уровень серьезности группы: от хобби до профессиональной деятельности.
    """
    HOBBY = "Хобби (редкие репетиции)"
    SEMI_PRO = "Полупрофессионально (концерты, записи)"
    PRO = "Профессионально (основной доход, турне)"

    @classmethod
    def list_values(cls):
        return [member.value for member in cls]