from prometheus_client import Histogram

# Время прохождения регистрации
registration_duration = Histogram(
    "app_registration_duration_seconds",
    "Время прохождения регистрации",
    ["source"] # bot\web
)

# Время на каждом шаге (имя, город, инструменты, жанры, контакты)
registration_step_duration = Histogram(
    "registration_step_duration_seconds",
    "Время, затраченное пользователем на каждый шаг регистрации",
    ["source", "step"]
)