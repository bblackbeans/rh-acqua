# Generated manually to fix recruiter foreign key

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0001_initial'),
        ('users', '0008_fix_admin_log'),
    ]

    operations = [
        migrations.RunSQL(
            # Remove a foreign key constraint antiga
            "ALTER TABLE vacancies_vacancy DROP CONSTRAINT IF EXISTS vacancies_vacancy_recruiter_id_77df4afa_fk_auth_user_id;",
            # Reverter se necessário
            "ALTER TABLE vacancies_vacancy ADD CONSTRAINT vacancies_vacancy_recruiter_id_77df4afa_fk_auth_user_id FOREIGN KEY (recruiter_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;"
        ),
        migrations.RunSQL(
            # Adiciona a nova foreign key constraint para users_user
            "ALTER TABLE vacancies_vacancy ADD CONSTRAINT vacancies_vacancy_recruiter_id_77df4afa_fk_users_user_id FOREIGN KEY (recruiter_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;",
            # Reverter se necessário
            "ALTER TABLE vacancies_vacancy DROP CONSTRAINT IF EXISTS vacancies_vacancy_recruiter_id_77df4afa_fk_users_user_id;"
        ),
    ]
