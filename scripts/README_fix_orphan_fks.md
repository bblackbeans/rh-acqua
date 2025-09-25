# Fix Orphan User Foreign Keys

## Problema

Erro: `psycopg2.errors.ForeignKeyViolation: insert or update on table "users_education" violates foreign key constraint`

**Causa:** Registros nas tabelas do currículo (users_education, users_experience, etc.) referenciam user_id que não existe na tabela users_user.

## Solução

### 1. Auditoria (Dry-run)

```bash
# Verificar órfãos sem aplicar correções
python manage.py fix_orphan_user_fks
```

### 2. Correção Automática

```bash
# Corrigir órfãos criando usuário fallback automático
python manage.py fix_orphan_user_fks --apply

# Ou usar usuário existente específico como fallback
python manage.py fix_orphan_user_fks --apply --fallback-user-id 1
```

### 3. Auditoria via SQL (Opcional)

```bash
# Se tiver acesso direto ao PostgreSQL
psql -U $DB_USER -d $DB_NAME -f scripts/auditar_orfaos_auth_user.sql
```

## Como Funciona

1. **Identifica órfãos:** Busca user_id em tabelas que não existem em users_user
2. **Relatório:** Lista quantos registros órfãos por tabela/user_id
3. **Correção:** Reatribui órfãos para usuário fallback (preserva dados)
4. **Transação:** Tudo em transação atômica

## Tabelas Verificadas

- users_education
- users_experience  
- users_technicalskill
- users_softskill
- users_certification
- users_language

## Usuário Fallback

Por padrão cria: `fallback.bot@system.local`
- Role: candidate
- Nome: Fallback Bot
- Ativo: true

## Exemplo de Saída

```
==> Modo: DRY-RUN
Auditando tabelas...
❌ Órfãos encontrados (total=3):
- users_education
    user_id=15 -> 1 registros
- users_experience  
    user_id=15 -> 2 registros
🔍 Dry-run concluído. Use --apply para corrigir.
```

## Após Correção

- Admin funcionará sem erro 500
- Novos inserts não falharão por FK violation
- Dados órfãos preservados e reatribuídos 