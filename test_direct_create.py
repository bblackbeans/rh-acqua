#!/usr/bin/env python3
"""
Script para testar criação direta de vaga
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from vacancies.models import Vacancy, Hospital, Department, Skill
from users.models import User

def test_direct_create():
    """Testa criação direta de vaga"""
    print("=== TESTE DE CRIAÇÃO DIRETA ===")
    
    try:
        # Obter objetos necessários
        hospital = Hospital.objects.get(id=2)  # Hospital São Lucas
        dept = Department.objects.filter(hospital=hospital).first()  # Primeiro departamento
        skill = Skill.objects.get(id=1)
        user = User.objects.get(id=9)  # Usuário admin
        
        print(f"Hospital: {hospital.name}")
        print(f"Departamento: {dept.name}")
        print(f"Skill: {skill.name}")
        print(f"Usuário: {user.email}")
        
        # Criar vaga diretamente
        print("\nCriando vaga...")
        vacancy = Vacancy.objects.create(
            title='Teste Direto',
            slug='teste-direto-hospital-central',  # Slug explícito
            description='Descrição de teste',
            requirements='Requisitos de teste',
            hospital=hospital,
            department=dept,
            location='SP',
            recruiter=user,
            # category=None,  # Não definir categoria
            status='published',
            contract_type='full_time',
            experience_level='mid'
        )
        
        print(f"✅ Vaga criada com sucesso! ID: {vacancy.id}")
        print(f"Slug: {vacancy.slug}")
        
        # Adicionar skills depois
        print("\nAdicionando skills...")
        vacancy.skills.add(skill)
        print(f"Skills: {list(vacancy.skills.all())}")
        
        # Verificar objeto final
        print(f"\nObjeto final:")
        print(f"  ID: {vacancy.id}")
        print(f"  Título: {vacancy.title}")
        print(f"  Hospital: {vacancy.hospital}")
        print(f"  Departamento: {vacancy.department}")
        print(f"  Recrutador: {vacancy.recruiter}")
        print(f"  Status: {vacancy.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_direct_create()
    if success:
        print("\n🎉 Teste de criação direta PASSOU!")
    else:
        print("\n💥 Teste de criação direta FALHOU!") 