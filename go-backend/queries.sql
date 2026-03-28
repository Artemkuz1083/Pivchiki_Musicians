-- queries.sql

-- --- AUTH QUERIES ---

-- name: CreateAccount :one
INSERT INTO accounts (login, password_hash)
VALUES ($1, $2)
RETURNING id;

-- name: GetAccountByLogin :one
SELECT id, login, password_hash 
FROM accounts 
WHERE login = $1 LIMIT 1;

-- name: CheckAccountExists :one
SELECT EXISTS(SELECT 1 FROM accounts WHERE login = $1);

-- --- USER PROFILE QUERIES ---

-- name: GetUser :one
-- Получение одного профиля по ID
SELECT id, name, city, age, contacts, theoretical_knowledge_level, has_performance_experience, about_me, external_link, is_visible, photo_path, audio_path 
FROM public.users
WHERE id = $1 LIMIT 1;

-- name: CreateUserProfile :exec
INSERT INTO users (id, name, city, age, contacts, theoretical_knowledge_level, has_performance_experience, about_me, external_link, is_visible)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);

-- name: UpdateUserProfile :exec
-- Получаем обновленный профиль у юзера
UPDATE users
SET 
    name = COALESCE($2, name),
    city = COALESCE($3, city),
    age = COALESCE($4, age),
    contacts = COALESCE($5, contacts),
    theoretical_knowledge_level = COALESCE($6, theoretical_knowledge_level),
    has_performance_experience = COALESCE($7, has_performance_experience),
    about_me = COALESCE($8, about_me),
    external_link = COALESCE($9, external_link),
    is_visible = COALESCE(sqlc.narg('is_visible'), is_visible)
WHERE id = $1;

-- --- INSTRUMENTS ---

-- name: AddUserInstrument :exec
INSERT INTO instruments (user_id, name, proficiency_level) 
VALUES ($1, $2, $3);

-- name: GetUserInstruments :many
-- Получаем инструменты и уровни владения
SELECT name, proficiency_level 
FROM public.instruments 
WHERE user_id = $1;

-- name: DeleteUserInstruments :exec
DELETE FROM instruments WHERE user_id = $1;

-- --- GENRES ---

-- name: AddUserGenre :exec
INSERT INTO user_genres (user_id, name) 
VALUES ($1, $2);

-- name: GetUserGenres :many
-- Получаем все жанры пользователя одним списком строк
SELECT name 
FROM public.user_genres 
WHERE user_id = $1;

-- name: DeleteUserGenres :exec
DELETE FROM user_genres WHERE user_id = $1;