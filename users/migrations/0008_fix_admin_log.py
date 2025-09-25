from django.db import migrations, models
import django.db.models.deletion

def fix_admin_log_foreign_key(apps, schema_editor):
    """Corrige a foreign key da tabela django_admin_log para usar o modelo customizado."""
    # Esta migração corrige o problema de foreign key constraint
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_language_unique_together'),
    ]

    operations = [
        # Remove a constraint antiga se existir
        migrations.RunSQL(
            sql="""
            ALTER TABLE django_admin_log 
            DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_auth_user_id;
            """,
            reverse_sql="""
            ALTER TABLE django_admin_log 
            ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id 
            FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;
            """
        ),
        # Adiciona a nova constraint para o modelo customizado
        migrations.RunSQL(
            sql="""
            ALTER TABLE django_admin_log 
            ADD CONSTRAINT django_admin_log_user_id_fk 
            FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE django_admin_log 
            DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fk;
            """
        ),
        # Executa a função de correção
        migrations.RunPython(fix_admin_log_foreign_key, reverse_code=migrations.RunPython.noop),
    ] 