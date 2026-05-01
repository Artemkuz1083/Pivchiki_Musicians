-- 1. Системные таблицы
CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Профили
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    name TEXT,
    city TEXT,
    age INTEGER,
    contacts TEXT,
    theoretical_knowledge_level INTEGER,
    has_performance_experience TEXT,
    about_me TEXT,
    external_link TEXT,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    photo_path TEXT,
    audio_path TEXT
);

CREATE TABLE IF NOT EXISTS group_profiles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT,
    formation_date INTEGER,
    platforms TEXT[],
    description TEXT,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    seriousness_level TEXT,
    financial_status TEXT,
    concerts JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Связи (Участники, Инструменты, Жанры)
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL REFERENCES group_profiles(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(group_id, user_id)
);

CREATE TABLE IF NOT EXISTS instruments (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    proficiency_level INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_genres (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS group_genres (
    id SERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL REFERENCES group_profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);

-- 4. СИСТЕМА ЛАЙКОВ (Три таблицы без дублей)
CREATE TABLE IF NOT EXISTS user_likes_user (
    id SERIAL PRIMARY KEY,
    swiper_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(swiper_user_id, target_user_id)
);

CREATE TABLE IF NOT EXISTS user_likes_group (
    id SERIAL PRIMARY KEY,
    swiper_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_group_id BIGINT NOT NULL REFERENCES group_profiles(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(swiper_user_id, target_group_id)
);

CREATE TABLE IF NOT EXISTS group_likes_user (
    id SERIAL PRIMARY KEY,
    swiper_group_id BIGINT NOT NULL REFERENCES group_profiles(id) ON DELETE CASCADE,
    target_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(swiper_group_id, target_user_id)
);

-- 5. Инвайты
CREATE TABLE IF NOT EXISTS group_invitations (
    id SERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL REFERENCES group_profiles(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(group_id, user_id)
);