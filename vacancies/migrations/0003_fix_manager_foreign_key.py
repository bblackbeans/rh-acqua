# Generated manually to fix manager foreign key

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0002_fix_recruiter_foreign_key'),
        ('users', '0008_fix_admin_log'),
    ]

    operations = [
        migrations.RunSQL(
            # Remove a foreign key constraint antiga
            "ALTER TABLE vacancies_department DROP CONSTRAINT IF EXISTS vacancies_department_manager_id_3369d3d5_fk_auth_user_id;",
            # Reverter se necessário
            "ALTER TABLE vacancies_department ADD CONSTRAINT vacancies_department_manager_id_3369d3d5_fk_auth_user_id FOREIGN KEY (manager_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;"
        ),
        migrations.RunSQL(
            # Adiciona a nova foreign key constraint para users_user
            "ALTER TABLE vacancies_department ADD CONSTRAINT vacancies_department_manager_id_3369d3d5_fk_users_user_id FOREIGN KEY (manager_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;",
            # Reverter se necessário
            "ALTER TABLE vacancies_department DROP CONSTRAINT IF EXISTS vacancies_department_manager_id_3369d3d5_fk_users_user_id;"
        ),
    ]
