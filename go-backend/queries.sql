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

-- name: CheckProfileExists :one
SELECT EXISTS(SELECT 1 FROM public.users WHERE id = $1);

-- --- USER PROFILE QUERIES ---

-- name: GetUser :one
-- Получение одного профиля по ID
SELECT id, name, city, age, contacts, theoretical_knowledge_level, has_performance_experience, about_me, external_link, is_visible, photo_path, audio_path 
FROM public.users
WHERE id = $1 LIMIT 1;

-- name: GetFeedProfiles :many
SELECT 
    u.id, u.name, u.city, u.age, u.contacts, u.theoretical_knowledge_level, 
    u.has_performance_experience, u.about_me, u.external_link, u.is_visible,
    u.photo_path, u.audio_path,
    COALESCE(
        (SELECT array_agg(ug.name)::text[] FROM user_genres ug WHERE ug.user_id = u.id), 
        '{}'::text[]
    ) as genres,
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('name', i.name, 'proficiency_level', i.proficiency_level)) 
         FROM instruments i WHERE i.user_id = u.id), 
        '[]'::jsonb
    ) as instruments
FROM public.users u
WHERE u.id != $1 
  AND u.is_visible = true
  AND (cardinality(sqlc.arg('cities')::text[]) = 0 OR u.city = ANY(sqlc.arg('cities')::text[]))
  AND (cardinality(sqlc.arg('genres')::text[]) = 0 OR EXISTS (
      SELECT 1 FROM user_genres ug WHERE ug.user_id = u.id AND ug.name = ANY(sqlc.arg('genres')::text[])
  ))
  AND (cardinality(sqlc.arg('instruments')::text[]) = 0 OR EXISTS (
      SELECT 1 FROM instruments i WHERE i.user_id = u.id 
      AND i.name = ANY(sqlc.arg('instruments')::text[])
      AND (sqlc.narg('min_proficiency')::int IS NULL OR i.proficiency_level >= sqlc.narg('min_proficiency'))
  ))
  AND (sqlc.narg('has_exp')::text IS NULL OR u.has_performance_experience = sqlc.narg('has_exp')::text)
  AND (sqlc.narg('theory_level')::int IS NULL OR u.theoretical_knowledge_level >= sqlc.narg('theory_level'))
  AND NOT EXISTS (
      SELECT 1 FROM user_likes_user ul WHERE ul.swiper_user_id = $1 AND ul.target_user_id = u.id
  )
ORDER BY RANDOM()
LIMIT $2;

-- name: GetPublicFeed :many
-- Получение профилей для неавторизованных пользователей
SELECT 
    u.id, u.name, u.city, u.age, u.contacts, u.theoretical_knowledge_level, 
    u.has_performance_experience, u.about_me, u.external_link, u.is_visible,
    u.photo_path, u.audio_path,
    COALESCE(
        (SELECT array_agg(ug.name)::text[] FROM user_genres ug WHERE ug.user_id = u.id), 
        '{}'::text[]
    ) as genres,
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object(
            'name', i.name, 
            'proficiency_level', i.proficiency_level
        )) FROM instruments i WHERE i.user_id = u.id), 
        '[]'::jsonb
    ) as instruments
FROM public.users u
WHERE u.is_visible = true
ORDER BY RANDOM()
LIMIT $1;

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
    is_visible = COALESCE(sqlc.narg('is_visible'), is_visible),
    photo_path = COALESCE(sqlc.narg('photo_path'), photo_path),
    audio_path = COALESCE(sqlc.narg('audio_path'), audio_path)
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

-- name: AddInteraction :exec
-- Добавляем лайк или дизлайк. Используем ON CONFLICT, чтобы избежать ошибок при повторном свайпе
INSERT INTO user_likes_user (swiper_user_id, target_user_id, action)
VALUES ($1, $2, $3)
ON CONFLICT (swiper_user_id, target_user_id) 
DO UPDATE SET action = EXCLUDED.action, created_at = NOW();

-- name: CheckMatch :one
-- Проверяем, лайкал ли нас этот пользователь в ответ
SELECT EXISTS (
    SELECT 1 FROM user_likes_user 
    WHERE swiper_user_id = $1 AND target_user_id = $2 AND action = 'like'
);