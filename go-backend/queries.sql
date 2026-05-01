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
SELECT * FROM public.users WHERE id = $1 LIMIT 1;

-- name: CreateUserProfile :exec
INSERT INTO users (id, name, city, age, contacts, theoretical_knowledge_level, has_performance_experience, about_me, external_link, is_visible)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);

-- name: UpdateUserProfile :exec
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

-- name: GetFeedProfiles :many
SELECT 
    u.*,
    COALESCE((SELECT array_agg(ug.name)::text[] FROM user_genres ug WHERE ug.user_id = u.id), '{}'::text[]) as genres,
    COALESCE((SELECT jsonb_agg(jsonb_build_object('name', i.name, 'proficiency_level', i.proficiency_level)) FROM instruments i WHERE i.user_id = u.id), '[]'::jsonb) as instruments
FROM users u
WHERE u.id != $1 
  AND u.is_visible = true
  AND (cardinality(sqlc.arg('cities')::text[]) = 0 OR u.city = ANY(sqlc.arg('cities')::text[]))
  AND (cardinality(sqlc.arg('genres')::text[]) = 0 OR EXISTS (
      SELECT 1 FROM user_genres ug WHERE ug.user_id = u.id AND ug.name = ANY(sqlc.arg('genres')::text[])
  ))
  -- ВОТ ЭТИ ПОЛЯ НУЖНЫ ДЛЯ ТВОЕГО РЕПО:
  AND (cardinality(sqlc.arg('instruments')::text[]) = 0 OR EXISTS (
      SELECT 1 FROM instruments i WHERE i.user_id = u.id AND i.name = ANY(sqlc.arg('instruments')::text[])
  ))
  AND (sqlc.narg('min_proficiency')::int IS NULL OR EXISTS (
      SELECT 1 FROM instruments i WHERE i.user_id = u.id AND i.proficiency_level >= sqlc.narg('min_proficiency')
  ))
  AND (sqlc.narg('theory_level')::int IS NULL OR u.theoretical_knowledge_level >= sqlc.narg('theory_level'))
  AND (sqlc.narg('has_exp')::text IS NULL OR u.has_performance_experience = sqlc.narg('has_exp'))
  -- Конец фильтров
  AND NOT EXISTS (
      SELECT 1 FROM user_likes_user ul WHERE ul.swiper_user_id = $1 AND ul.target_user_id = u.id
  )
ORDER BY RANDOM()
LIMIT $2;

-- name: CheckMatch :one
-- Возвращаем обратно этот метод для репозитория
SELECT EXISTS (
    SELECT 1 FROM user_likes_user 
    WHERE swiper_user_id = $1 AND target_user_id = $2 AND action = 'like'
);

-- name: GetPublicFeed :many
SELECT 
    u.*,
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
WHERE u.is_visible = true
ORDER BY RANDOM()
LIMIT $1;

-- --- GROUP QUERIES ---

-- name: CreateGroupProfile :one
INSERT INTO group_profiles (
    name, city, formation_date, platforms, description, is_visible, seriousness_level, financial_status, concerts
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9
) RETURNING id;

-- name: GetGroup :one
SELECT * FROM group_profiles WHERE id = $1 LIMIT 1;

-- name: UpdateGroupProfile :exec
UPDATE group_profiles
SET 
    name = COALESCE($2, name),
    city = COALESCE($3, city),
    formation_date = COALESCE($4, formation_date),
    platforms = COALESCE($5, platforms),
    description = COALESCE($6, description),
    is_visible = COALESCE(sqlc.narg('is_visible'), is_visible),
    seriousness_level = COALESCE($7, seriousness_level),
    financial_status = COALESCE($8, financial_status),
    concerts = COALESCE($9, concerts)
WHERE id = $1;

-- name: GetGroupFeed :many
SELECT 
    g.*,
    COALESCE((SELECT array_agg(gg.name)::text[] FROM group_genres gg WHERE gg.group_id = g.id), '{}'::text[]) as genres,
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('user_id', gm.user_id, 'name', u.name, 'role', gm.role)) 
         FROM group_members gm JOIN users u ON u.id = gm.user_id WHERE gm.group_id = g.id), 
        '[]'::jsonb
    ) as members
FROM group_profiles g
WHERE g.is_visible = true
  AND (cardinality(sqlc.arg('cities')::text[]) = 0 OR g.city = ANY(sqlc.arg('cities')::text[]))
  AND NOT EXISTS (
      SELECT 1 FROM user_likes_group ulg WHERE ulg.swiper_user_id = $1 AND ulg.target_group_id = g.id
  )
ORDER BY RANDOM()
LIMIT $2;

-- name: GetPublicGroupFeed :many
SELECT 
    g.*,
    COALESCE((SELECT array_agg(gg.name)::text[] FROM group_genres gg WHERE gg.group_id = g.id), '{}'::text[]) as genres,
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object('user_id', gm.user_id, 'name', u.name, 'role', gm.role)) 
         FROM group_members gm JOIN users u ON u.id = gm.user_id WHERE gm.group_id = g.id), 
        '[]'::jsonb
    ) as members
FROM group_profiles g
WHERE g.is_visible = true
ORDER BY RANDOM()
LIMIT $1;

-- --- LIKE & MATCH QUERIES ---

-- name: AddInteraction :exec
INSERT INTO user_likes_user (swiper_user_id, target_user_id, action)
VALUES ($1, $2, $3)
ON CONFLICT (swiper_user_id, target_user_id) 
DO UPDATE SET action = EXCLUDED.action, created_at = NOW();

-- name: AddGroupInteraction :exec
-- Пользователь -> Группа
INSERT INTO user_likes_group (swiper_user_id, target_group_id, action)
VALUES ($1, $2, $3)
ON CONFLICT (swiper_user_id, target_group_id) 
DO UPDATE SET action = EXCLUDED.action, created_at = NOW();

-- name: AddGroupLikeUser :exec
-- Группа (админ) -> Пользователь
INSERT INTO group_likes_user (swiper_group_id, target_user_id, action)
VALUES ($1, $2, $3)
ON CONFLICT (swiper_group_id, target_user_id) 
DO UPDATE SET action = EXCLUDED.action, created_at = NOW();

-- name: GetUserMatches :many
-- Взаимные лайки музыкантов
SELECT 
    l1.target_user_id as match_id
FROM user_likes_user l1
INNER JOIN user_likes_user l2 ON 
    l1.target_user_id = l2.swiper_user_id AND 
    l1.swiper_user_id = l2.target_user_id
WHERE 
    l1.swiper_user_id = $1 
    AND l1.action = 'like' 
    AND l2.action = 'like';

-- name: GetGroupMatches :many
-- Взаимные лайки между юзером и группой
SELECT 
    g.*,
    COALESCE((SELECT array_agg(gg.name)::text[] FROM group_genres gg WHERE gg.group_id = g.id), '{}'::text[]) as genres
FROM group_profiles g
INNER JOIN user_likes_group ulg ON g.id = ulg.target_group_id
INNER JOIN group_likes_user glu ON g.id = glu.swiper_group_id
WHERE ulg.swiper_user_id = $1 
  AND glu.target_user_id = $1
  AND ulg.action = 'like'
  AND glu.action = 'like';

-- --- OTHER ---

-- name: AddUserInstrument :exec
INSERT INTO instruments (user_id, name, proficiency_level) VALUES ($1, $2, $3);

-- name: DeleteUserInstruments :exec
DELETE FROM instruments WHERE user_id = $1;

-- name: GetUserGenres :many
-- Получаем все жанры пользователя одним списком строк
SELECT name FROM public.user_genres WHERE user_id = $1;

-- name: GetGroupGenres :many
-- Получаем все жанры группы
SELECT name FROM public.group_genres WHERE group_id = $1;

-- name: GetUserInstruments :many
-- Получаем инструменты и уровни владения
SELECT name, proficiency_level FROM public.instruments WHERE user_id = $1;

-- name: AddUserGenre :exec
INSERT INTO user_genres (user_id, name) VALUES ($1, $2);

-- name: DeleteUserGenres :exec
DELETE FROM user_genres WHERE user_id = $1;

-- name: DeleteGroupProfile :exec
DELETE FROM group_profiles WHERE id = $1;

-- name: AddGroupGenre :exec
INSERT INTO group_genres (group_id, name) VALUES ($1, $2);

-- name: DeleteGroupGenres :exec
DELETE FROM group_genres WHERE group_id = $1;

-- name: AddGroupMember :exec
INSERT INTO group_members (
    group_id, user_id, role, is_admin
) VALUES (
    $1, $2, $3, $4
);

-- name: RemoveMemberFromGroup :exec
DELETE FROM group_members WHERE group_id = $1 AND user_id = $2;

-- name: UpdateMemberRole :exec
UPDATE group_members SET role = $3 WHERE group_id = $1 AND user_id = $2;

-- name: GetGroupMembers :many
-- Получение списка участников группы с их именами
SELECT gm.user_id, u.name, gm.role, gm.is_admin FROM group_members gm JOIN users u ON u.id = gm.user_id WHERE gm.group_id = $1;

-- name: GetUserGroups :many
SELECT g.id, g.name, gm.role, gm.is_admin
FROM group_profiles g
JOIN group_members gm ON g.id = gm.group_id
WHERE gm.user_id = $1;

-- name: CreateInvitation :one
INSERT INTO group_invitations (group_id, user_id, role, status)
VALUES ($1, $2, $3, 'PENDING')
RETURNING id;

-- name: CancelInvitation :exec
DELETE FROM group_invitations 
WHERE id = $1 AND group_id = $2;

-- name: GetUserInvitations :many
SELECT i.id, i.group_id, g.name as group_name, i.role, i.created_at
FROM group_invitations i
JOIN group_profiles g ON g.id = i.group_id
WHERE i.user_id = $1 AND i.status = 'PENDING';

-- name: RespondToInvitation :one
UPDATE group_invitations 
SET status = $2 
WHERE id = $1 AND user_id = $3
RETURNING group_id, role;