# users/management/commands/fix_orphan_user_fks.py
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

TABLES = [
    ("users_education", "user_id"),
    ("users_experience", "user_id"),
    ("users_technicalskill", "user_id"),
    ("users_softskill", "user_id"),
    ("users_certification", "user_id"),
    ("users_language", "user_id"),
]

SQL_FIND_ORPHANS = """
SELECT t.table_name, t.user_col, x.{user_col} AS bad_user_id, COUNT(*) AS rows
FROM (
  SELECT %s AS table_name, %s AS user_col
) AS t
JOIN {table} x ON TRUE
LEFT JOIN {user_table} u ON u.id = x.{user_col}
WHERE u.id IS NULL
GROUP BY t.table_name, t.user_col, x.{user_col}
ORDER BY t.table_name, bad_user_id;
"""

SQL_ROWS_WITH_USER = "SELECT id FROM {table} WHERE {user_col} = %s"

SQL_UPDATE_USER = "UPDATE {table} SET {user_col} = %s WHERE id = ANY(%s)"

class Command(BaseCommand):
    help = "Audita e corrige FKs órfãs para auth_user (dry-run por padrão)."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Aplica correções (sem isso, apenas dry-run).")
        parser.add_argument("--fallback-user-id", type=int, help="ID do usuário fallback (se omitir, cria/usa 'fallback.bot@system.local').")

    def get_or_create_fallback_user(self, fallback_user_id=None):
        if fallback_user_id:
            try:
                return User.objects.get(id=fallback_user_id)
            except User.DoesNotExist:
                raise SystemExit(f"Fallback user id={fallback_user_id} não existe.")

        # padrão: criar/usar um usuário técnico
        email = "fallback.bot@system.local"
        u, created = User.objects.get_or_create(
            email=email,
            defaults={
                "is_active": True, 
                "date_joined": timezone.now(),
                "role": "candidate",  # Assumindo que role é obrigatório
                "first_name": "Fallback",
                "last_name": "Bot"
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Criado usuário fallback: {email} (id={u.id})"))
        return u

    def handle(self, *args, **opts):
        apply = opts["apply"]
        self.stdout.write(self.style.NOTICE(f"==> Modo: {'APLICAR' if apply else 'DRY-RUN'}"))

        with connection.cursor() as cur:
            user_table = User._meta.db_table  # tabela real do User
            total_orphans = 0
            per_table = {}

            # AUDITORIA
            self.stdout.write(self.style.NOTICE("Auditando tabelas..."))
            for table, col in TABLES:
                try:
                    q = SQL_FIND_ORPHANS.format(table=table, user_col=col, user_table=user_table)
                    cur.execute(q, [table, col])
                    rows = cur.fetchall()
                    per_table[table] = rows
                    for r in rows:
                        # (table_name, user_col, bad_user_id, count)
                        total_orphans += r[3]
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Erro ao auditar {table}: {e}"))
                    per_table[table] = []

            # RELATÓRIO
            if total_orphans == 0:
                self.stdout.write(self.style.SUCCESS("✅ Nenhum órfão encontrado."))
                return

            self.stdout.write(self.style.WARNING(f"❌ Órfãos encontrados (total={total_orphans}):"))
            for table, rows in per_table.items():
                if not rows:
                    continue
                self.stdout.write(self.style.WARNING(f"- {table}"))
                for _, user_col, bad_user_id, cnt in rows:
                    self.stdout.write(f"    user_id={bad_user_id} -> {cnt} registros")

            if not apply:
                self.stdout.write(self.style.NOTICE("🔍 Dry-run concluído. Use --apply para corrigir."))
                return

            # CORREÇÃO
            fallback_user = self.get_or_create_fallback_user(opts.get("fallback_user_id"))
            self.stdout.write(self.style.NOTICE(f"🔧 Usando fallback user id={fallback_user.id} ({fallback_user.email})"))

            with transaction.atomic():
                total_fixed = 0
                for table, col in TABLES:
                    # quem está órfão nessa tabela?
                    try:
                        q = SQL_FIND_ORPHANS.format(table=table, user_col=col, user_table=user_table)
                        cur.execute(q, [table, col])
                        rows = cur.fetchall()
                        if not rows:
                            continue

                        # para cada bad_user_id, buscar IDs e atualizar
                        for _, user_col, bad_user_id, _ in rows:
                            cur.execute(SQL_ROWS_WITH_USER.format(table=table, user_col=user_col), [bad_user_id])
                            ids = [r[0] for r in cur.fetchall()]
                            if not ids:
                                continue
                            cur.execute(SQL_UPDATE_USER.format(table=table, user_col=user_col), [fallback_user.id, ids])
                            total_fixed += len(ids)
                            self.stdout.write(self.style.SUCCESS(
                                f"✅ [{table}] {len(ids)} linhas: {user_col} {bad_user_id} -> {fallback_user.id}"
                            ))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Erro ao corrigir {table}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"🎉 Correção concluída: {total_fixed} registros corrigidos.")) 