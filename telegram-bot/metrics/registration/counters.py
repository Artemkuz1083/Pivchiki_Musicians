from prometheus_client import Counter

# Кол-во начавших регистрацию
registration_started = Counter(
    "app_registration_started_total",
    "Количество начатых регистраций",
    ["source"]  # bot / web
)

# Кол-во закончивших регистрацию
registration_success = Counter(
    "app_registration_success_total",
    "Количество успешно завершённых регистраций",
    ["source"] # bot / web
)

# Кол-во дошедших до введения имени
registration_username = Counter(
    "app_registration_username",
    "Количество дошедших до введения имени",
    ["source"] # bot / web
)

# Кол-во дошедших до введения города
registration_city = Counter(
    "app_registration_city",
    "Количество дошедших до введения города",
    ["source"] # bot / web
)

# Кол-во дошедших до введения инструмента
registration_instrument = Counter(
    "app_registration_instrument",
    "Количество дошедших до введения инструмента",
    ["source"] # bot / web
)

# Кол-во дошедших до знаний об инструменте
registration_instrument_rating = Counter(
    "app_registration_instrument_rating",
    "Количество дошедших до знаний об инструменте",
    ["source"] # bot / web
)

# Кол-во дошедших до жанров
registration_genre = Counter(
    "app_registration_genre",
    "Количество дошедших до жанров",
    ["source"] # bot / web
)

# Кол-во дошедших до контактов
registration_contacts = Counter(
    "app_registration_contacts",
    "Количество дошедших до контактов",
    ["source"] # bot / web
)

# Кол-во ошибок во время регистрации
registration_errors = Counter(
    "app_registration_errors_total",
    "Количество ошибок при регистрации",
    ["source", "step"]  # шаг регистрации: name, city, instrument, genre, contacts
)

