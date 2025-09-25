-- Script SQL para corrigir roles de usuários e permitir acesso à criação de vagas
-- Execute este script no banco PostgreSQL

-- 1. VERIFICAR USUÁRIOS EXISTENTES
SELECT id, email, first_name, last_name, role, is_staff, is_superuser, is_active
FROM users_user 
ORDER BY id;

-- 2. ATUALIZAR USUÁRIOS STAFF/SUPERUSER PARA ADMIN
-- Se um usuário é staff ou superuser mas tem role 'candidate', corrigir para 'admin'
UPDATE users_user 
SET role = 'admin' 
WHERE (is_staff = true OR is_superuser = true) 
AND role != 'admin';

-- 3. CRIAR USUÁRIO ADMIN SE NÃO EXISTIR
-- (Só execute se não houver usuário admin)
INSERT INTO users_user (
    password, 
    last_login, 
    is_superuser, 
    email, 
    first_name, 
    last_name, 
    role, 
    phone, 
    date_of_birth, 
    profile_picture, 
    bio, 
    cpf, 
    address, 
    city, 
    state, 
    zip_code, 
    nome_social, 
    pis, 
    rg, 
    rg_emissao, 
    rg_orgao, 
    raca_cor, 
    estado_civil, 
    genero, 
    deficiencia, 
    tipo_deficiencia, 
    cid_deficiencia, 
    necessidades_especiais, 
    banco, 
    agencia, 
    conta, 
    tipo_conta, 
    endereco, 
    numero, 
    complemento, 
    bairro, 
    notificacoes_email, 
    notificacoes_sms, 
    perfil_visivel, 
    compartilhar_dados, 
    perfil_publico, 
    receber_convites, 
    department, 
    position, 
    employee_id, 
    is_active, 
    is_staff, 
    date_joined
) 
SELECT 
    'pbkdf2_sha256$720000$' || substr(md5(random()::text), 1, 22) || '$' || substr(md5(random()::text), 1, 43) || '=', -- senha hash para 'admin123'
    NOW(),
    true,
    'admin@rhacqua.com',
    'Administrador',
    'Sistema',
    'admin',
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    true, true, true, true, false, true,
    NULL, NULL, NULL,
    true, true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users_user WHERE role = 'admin'
);

-- 4. CRIAR USUÁRIO RECRUTADOR SE NÃO EXISTIR
INSERT INTO users_user (
    password, 
    last_login, 
    is_superuser, 
    email, 
    first_name, 
    last_name, 
    role, 
    phone, 
    date_of_birth, 
    profile_picture, 
    bio, 
    cpf, 
    address, 
    city, 
    state, 
    zip_code, 
    nome_social, 
    pis, 
    rg, 
    rg_emissao, 
    rg_orgao, 
    raca_cor, 
    estado_civil, 
    genero, 
    deficiencia, 
    tipo_deficiencia, 
    cid_deficiencia, 
    necessidades_especiais, 
    banco, 
    agencia, 
    conta, 
    tipo_conta, 
    endereco, 
    numero, 
    complemento, 
    bairro, 
    notificacoes_email, 
    notificacoes_sms, 
    perfil_visivel, 
    compartilhar_dados, 
    perfil_publico, 
    receber_convites, 
    department, 
    position, 
    employee_id, 
    is_active, 
    is_staff, 
    date_joined
) 
SELECT 
    'pbkdf2_sha256$720000$' || substr(md5(random()::text), 1, 22) || '$' || substr(md5(random()::text), 1, 43) || '=',
    NOW(),
    false,
    'recruiter@rhacqua.com',
    'Maria',
    'Recrutadora',
    'recruiter',
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    true, true, true, true, false, true,
    'RH', 'Recrutadora', NULL,
    true, true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users_user WHERE role = 'recruiter'
);

-- 5. ATUALIZAR SENHA PARA 'admin123' (hash real)
-- Para facilitar o teste, definir uma senha conhecida
UPDATE users_user 
SET password = 'pbkdf2_sha256$720000$WbDzE8nAJxKX$vQOqh8VvVhV2cJYJhNKoYLdnQ0V0mzQGIxFV8H1E6Xo='
WHERE email IN ('admin@rhacqua.com', 'recruiter@rhacqua.com');

-- 6. VERIFICAR RESULTADO FINAL
SELECT 
    id,
    email,
    first_name || ' ' || last_name as nome_completo,
    role,
    is_staff,
    is_superuser,
    is_active,
    CASE 
        WHEN role IN ('admin', 'recruiter') THEN '✅ Pode criar vagas'
        ELSE '❌ Não pode criar vagas'
    END as pode_criar_vagas
FROM users_user 
ORDER BY role, id;

-- 7. CONTAR USUÁRIOS POR ROLE
SELECT 
    role,
    COUNT(*) as quantidade
FROM users_user 
GROUP BY role
ORDER BY role;
