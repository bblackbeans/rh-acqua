#!/usr/bin/env python3
"""
Script para verificar e criar usuário recrutador se necessário
"""

import os
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from users.models import User

def check_create_recruiter():
    """Verifica se o usuário recrutador existe e cria se necessário"""
    try:
        # Procura pelo usuário recrutador
        recruiter = User.objects.filter(email='recruiter@example.com').first()
        
        if recruiter:
            print(f"✅ Usuário recrutador encontrado:")
            print(f"   Email: {recruiter.email}")
            print(f"   Nome: {recruiter.first_name} {recruiter.last_name}")
            print(f"   Role: {recruiter.role}")
            print(f"   Ativo: {recruiter.is_active}")
            print(f"   Último login: {recruiter.last_login}")
            
            # Verifica se a senha está correta
            if recruiter.check_password('recruiter123'):
                print("   ✅ Senha está correta")
            else:
                print("   ❌ Senha incorreta - redefinindo...")
                recruiter.set_password('recruiter123')
                recruiter.save()
                print("   ✅ Nova senha definida: recruiter123")
                
        else:
            print("❌ Usuário recrutador não encontrado. Criando...")
            
            # Cria novo usuário recrutador
            recruiter = User.objects.create_user(
                email='recruiter@example.com',
                password='recruiter123',
                first_name='João',
                last_name='Recrutador',
                role='recruiter',
                is_active=True
            )
            
            print(f"✅ Usuário recrutador criado com sucesso:")
            print(f"   Email: {recruiter.email}")
            print(f"   Senha: recruiter123")
            print(f"   Nome: {recruiter.first_name} {recruiter.last_name}")
            print(f"   Role: {recruiter.role}")
            
        # Lista todos os usuários para referência
        print(f"\n📋 Todos os usuários no sistema:")
        users = User.objects.all().order_by('role', 'email')
        for user in users:
            print(f"   - {user.email} ({user.first_name} {user.last_name}) - {user.role}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_create_recruiter() 