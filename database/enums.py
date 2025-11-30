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

class FinancialStatus(str, Enum):
    """
    Варианты финансового статуса группы
    """
    POOR = "Мы нищие"
    READY_TO_INVEST = "Готовы инвестировать"
    LIMITED_BUDGET = "Ограниченный бюджет"

    # возвращаем список финансовых статусов
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]

class Actions(str, Enum):
    """
    Список действий с анкетами
    """
    SKIP = "Skip"
    LIKE = "Like"