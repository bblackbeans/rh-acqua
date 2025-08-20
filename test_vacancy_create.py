#!/usr/bin/env python3
"""
Script de teste para criação de vaga
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from vacancies.models import Hospital, Department, Skill, Vacancy
from django.test.utils import override_settings

def test_vacancy_creation():
    """Testa a criação de uma vaga"""
    print("=== TESTE DE CRIAÇÃO DE VAGA ===")
    
    # Obter usuário recrutador
    User = get_user_model()
    try:
        user = User.objects.get(id=10)  # Usuário recrutador
        print(f"Usuário: {user.id} (Role: {getattr(user, 'role', 'N/A')})")
    except User.DoesNotExist:
        print("Usuário recrutador não encontrado!")
        return
    
    # Obter dados necessários
    try:
        hospital = Hospital.objects.first()
        dept = Department.objects.first()
        skill = Skill.objects.first()
        print(f"Hospital: {hospital.id} - {hospital.name}")
        print(f"Departamento: {dept.id} - {dept.name}")
        print(f"Habilidade: {skill.id} - {skill.name}")
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return
    
    # Criar cliente e fazer login
    client = Client()
    client.force_login(user)
    
    # Dados do POST
    post_data = {
        'title': 'Vaga Teste Automática',
        'description': 'Descrição de teste para verificar funcionamento',
        'requirements': 'Requisitos de teste',
        'hospital': hospital.id,
        'department': dept.id,
        'location': 'SP',
        'skills': [skill.id],
        'status': 'published',  # Usar 'published' em vez de 'PUBLISHED'
        'contract_type': 'full_time',  # Usar 'full_time' em vez de 'FULL_TIME'
        'experience_level': 'mid'  # Usar 'mid' em vez de 'mid_level'
    }
    
    print(f"\nDados do POST: {post_data}")
    
    # Fazer POST
    try:
        with override_settings(ALLOWED_HOSTS=['testserver']):
            response = client.post('/vacancies/recruiter/vacancy/create/', post_data)
            
            print(f"\n=== RESULTADO ===")
            print(f"Status Code: {response.status_code}")
            
            if hasattr(response, 'url') and response.url:
                print(f"Redirect URL: {response.url}")
            
            if response.context and 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print(f"Erros do formulário: {form.errors}")
                else:
                    print("Formulário válido!")
            else:
                print("Sem contexto de formulário")
                
            # Verificar se a vaga foi criada
            try:
                vacancy = Vacancy.objects.filter(title='Vaga Teste Automática').first()
                if vacancy:
                    print(f"✅ VAGA CRIADA COM SUCESSO!")
                    print(f"ID: {vacancy.id}")
                    print(f"Título: {vacancy.title}")
                    print(f"Recrutador: {vacancy.recruiter}")
                    print(f"Hospital: {vacancy.hospital}")
                    print(f"Skills: {list(vacancy.skills.all())}")
                else:
                    print("❌ Vaga não foi criada")
            except Exception as e:
                print(f"Erro ao verificar vaga: {e}")
                
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_vacancy_creation() 