# Generated manually to fix recruiter foreign key constraint

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0001_initial'),
    ]

    operations = [
        # Remove a constraint antiga do campo recruiter
        migrations.RunSQL(
            sql="PRAGMA foreign_keys=OFF;",
            reverse_sql="PRAGMA foreign_keys=ON;",
        ),
        # Recria o campo recruiter com a constraint correta
        migrations.RunSQL(
            sql="""
            CREATE TABLE vacancies_vacancy_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                slug VARCHAR(250) UNIQUE,
                description TEXT NOT NULL,
                requirements TEXT NOT NULL,
                benefits TEXT,
                hospital_id INTEGER NOT NULL,
                department_id INTEGER NOT NULL,
                category_id INTEGER,
                recruiter_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                contract_type VARCHAR(20) NOT NULL,
                experience_level VARCHAR(20) NOT NULL,
                salary_range_min DECIMAL(10,2),
                salary_range_max DECIMAL(10,2),
                is_salary_visible BOOLEAN NOT NULL,
                location VARCHAR(200) NOT NULL,
                is_remote BOOLEAN NOT NULL,
                publication_date DATE,
                closing_date DATE,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                views_count INTEGER NOT NULL,
                applications_count INTEGER NOT NULL,
                FOREIGN KEY (hospital_id) REFERENCES vacancies_hospital (id),
                FOREIGN KEY (department_id) REFERENCES vacancies_department (id),
                FOREIGN KEY (category_id) REFERENCES vacancies_jobcategory (id),
                FOREIGN KEY (recruiter_id) REFERENCES users_user (id)
            );
            """,
            reverse_sql="""
            DROP TABLE vacancies_vacancy_new;
            """,
        ),
        # Copia os dados da tabela antiga para a nova
        migrations.RunSQL(
            sql="""
            INSERT INTO vacancies_vacancy_new 
            SELECT * FROM vacancies_vacancy;
            """,
            reverse_sql="""
            INSERT INTO vacancies_vacancy 
            SELECT * FROM vacancies_vacancy_new;
            """,
        ),
        # Remove a tabela antiga e renomeia a nova
        migrations.RunSQL(
            sql="""
            DROP TABLE vacancies_vacancy;
            ALTER TABLE vacancies_vacancy_new RENAME TO vacancies_vacancy;
            """,
            reverse_sql="""
            ALTER TABLE vacancies_vacancy RENAME TO vacancies_vacancy_old;
            ALTER TABLE vacancies_vacancy_new RENAME TO vacancies_vacancy;
            """,
        ),
        # Reativa as foreign keys
        migrations.RunSQL(
            sql="PRAGMA foreign_keys=ON;",
            reverse_sql="PRAGMA foreign_keys=OFF;",
        ),
    ] 