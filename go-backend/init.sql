-- Таблица для системных аккаунтов (Auth)
CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Таблица пользователей (Профили)
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

-- Инструменты пользователя
CREATE TABLE IF NOT EXISTS instruments (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    proficiency_level INTEGER NOT NULL
);

-- Жанры пользователя
CREATE TABLE IF NOT EXISTS user_genres (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);

-- Таблица лайков (для будущего функционала)
CREATE TABLE IF NOT EXISTS user_likes_user (
    id SERIAL PRIMARY KEY,
    swiper_user_id BIGINT NOT NULL REFERENCES users(id),
    target_user_id BIGINT NOT NULL REFERENCES users(id),
    action TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);