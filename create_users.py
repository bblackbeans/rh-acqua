#!/usr/bin/env python3
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from users.models import User, CandidateProfile, RecruiterProfile

def create_users():
    """Cria usuários com diferentes roles para teste."""
    
    # Senha para todos os usuários
    password = 'admin123'
    
    # 1. Criar usuário ADMIN
    try:
        admin_user = User.objects.create_user(
            email='admin@rhacqua.com',
            password=password,
            first_name='João',
            last_name='Silva',
            role='admin',
            phone='(11) 99999-9999',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuário ADMIN criado: {admin_user.email}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário ADMIN: {e}")
    
    # 2. Criar usuário RECRUTADOR
    try:
        recruiter_user = User.objects.create_user(
            email='recruiter@rhacqua.com',
            password=password,
            first_name='Maria',
            last_name='Santos',
            role='recruiter',
            phone='(11) 88888-8888',
            department='Recursos Humanos',
            position='Recrutadora Sênior',
            employee_id='RH001'
        )
        
        # Criar perfil de recrutador
        RecruiterProfile.objects.create(
            user=recruiter_user,
            specialization='Tecnologia e Saúde',
            hiring_authority=True
        )
        print(f"✅ Usuário RECRUTADOR criado: {recruiter_user.email}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário RECRUTADOR: {e}")
    
    # 3. Criar usuário CANDIDATO
    try:
        candidate_user = User.objects.create_user(
            email='candidate@rhacqua.com',
            password=password,
            first_name='Pedro',
            last_name='Oliveira',
            role='candidate',
            phone='(11) 77777-7777',
            cpf='123.456.789-00',
            address='Rua das Flores, 123',
            city='São Paulo',
            state='SP',
            zip_code='01234-567'
        )
        
        # Criar perfil de candidato
        CandidateProfile.objects.create(
            user=candidate_user,
            education_level='Superior Completo',
            institution='Universidade de São Paulo',
            course='Administração',
            graduation_year=2020,
            years_of_experience=3,
            current_position='Analista Administrativo',
            current_company='Empresa ABC',
            skills='Gestão de processos, Excel avançado, SAP',
            desired_position='Coordenador Administrativo',
            desired_salary=5000.00,
            available_immediately=True
        )
        print(f"✅ Usuário CANDIDATO criado: {candidate_user.email}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário CANDIDATO: {e}")
    
    print("\n🎯 RESUMO DOS USUÁRIOS CRIADOS:")
    print("=" * 50)
    print("ADMIN:")
    print("  Email: admin@rhacqua.com")
    print("  Senha: admin123")
    print("  Nome: João Silva")
    print()
    print("RECRUTADOR:")
    print("  Email: recruiter@rhacqua.com")
    print("  Senha: admin123")
    print("  Nome: Maria Santos")
    print()
    print("CANDIDATO:")
    print("  Email: candidate@rhacqua.com")
    print("  Senha: admin123")
    print("  Nome: Pedro Oliveira")
    print()
    print("🔑 Todos os usuários usam a mesma senha: admin123")

if __name__ == '__main__':
    create_users() 