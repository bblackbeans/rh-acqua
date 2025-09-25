-- Auditoria de FKs órfãs para auth_user
-- Ajuste as tabelas conforme seu schema

WITH auth AS (SELECT id FROM users_user) -- Assumindo custom user model
SELECT 'users_education' AS table_name, user_id AS bad_user_id, COUNT(*) AS rows
FROM users_education e LEFT JOIN auth a ON a.id = e.user_id
WHERE a.id IS NULL
GROUP BY user_id

UNION ALL

SELECT 'users_experience', user_id, COUNT(*)
FROM users_experience x LEFT JOIN auth a ON a.id = x.user_id
WHERE a.id IS NULL
GROUP BY user_id

UNION ALL

SELECT 'users_technicalskill', user_id, COUNT(*)
FROM users_technicalskill s LEFT JOIN auth a ON a.id = s.user_id
WHERE a.id IS NULL
GROUP BY user_id

UNION ALL

SELECT 'users_softskill', user_id, COUNT(*)
FROM users_softskill s LEFT JOIN auth a ON a.id = s.user_id
WHERE a.id IS NULL
GROUP BY user_id

UNION ALL

SELECT 'users_certification', user_id, COUNT(*)
FROM users_certification c LEFT JOIN auth a ON a.id = c.user_id
WHERE a.id IS NULL
GROUP BY user_id

UNION ALL

SELECT 'users_language', user_id, COUNT(*)
FROM users_language l LEFT JOIN auth a ON a.id = l.user_id
WHERE a.id IS NULL
GROUP BY user_id

ORDER BY table_name, bad_user_id; 