from enum import Enum

class PerformanceExperience(str, Enum):
    """
    Варианты опытов выступления музыканта
    """
    NEVER = "Никогда не выступал"
    LOCAL_GIGS = "Давал локальные концерты"
    TOURS = "Ездил с гастролями"
    PROFESSIONAL = "Профессиональный музыкант"

    # возвращаем список опытов выступления
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]