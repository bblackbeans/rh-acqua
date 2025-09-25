#!/usr/bin/env python3
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

print("=== DEBUG USUÁRIOS ===")
print(f"User model: {User}")
print(f"USERNAME_FIELD: {User.USERNAME_FIELD}")
print(f"REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")

print("\n=== USUÁRIOS NO BANCO ===")
users = User.objects.all()
print(f"Total de usuários: {users.count()}")

for user in users[:5]:
    print(f"  - Email: {user.email}")
    print(f"    Nome: {user.get_full_name()}")
    print(f"    Ativo: {user.is_active}")
    print(f"    Staff: {user.is_staff}")
    print(f"    Superuser: {user.is_superuser}")
    print(f"    Role: {user.role}")
    print(f"    Último login: {user.last_login}")
    print()

print("\n=== TESTE DE AUTENTICAÇÃO ===")
# Testar autenticação com alguns usuários
test_users = User.objects.all()[:3]
for user in test_users:
    print(f"Testando usuário: {user.email}")
    # Testar com senha comum
    auth_user = authenticate(username=user.email, password='admin123')
    if auth_user:
        print(f"  ✅ Autenticação bem-sucedida com 'admin123'")
    else:
        print(f"  ❌ Falha na autenticação com 'admin123'")
    
    # Testar com senha vazia
    auth_user = authenticate(username=user.email, password='')
    if auth_user:
        print(f"  ✅ Autenticação bem-sucedida com senha vazia")
    else:
        print(f"  ❌ Falha na autenticação com senha vazia")
    print()
