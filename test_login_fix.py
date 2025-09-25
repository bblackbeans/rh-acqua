#!/usr/bin/env python3
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from django.contrib.auth import authenticate
from users.models import User

print("=== TESTE DE LOGIN APÓS CORREÇÃO ===")

# Testar com o usuário que você criou
test_email = 'kaue.ronald@gmail.com'
test_password = 'Krcandidato21'

print(f"Testando login com:")
print(f"  Email: {test_email}")
print(f"  Senha: {test_password}")

# Testar autenticação
user = authenticate(username=test_email, password=test_password)

if user:
    print(f"✅ LOGIN FUNCIONOU!")
    print(f"   Nome: {user.get_full_name()}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Ativo: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
else:
    print(f"❌ LOGIN FALHOU!")
    
    # Verificar se o usuário existe
    try:
        user_obj = User.objects.get(email=test_email)
        print(f"   Usuário existe no banco:")
        print(f"     Nome: {user_obj.get_full_name()}")
        print(f"     Ativo: {user_obj.is_active}")
        print(f"     Senha definida: {bool(user_obj.password)}")
        print(f"     Hash da senha: {user_obj.password[:50]}...")
        
        # Testar se a senha está correta
        from django.contrib.auth.hashers import check_password
        is_valid = check_password(test_password, user_obj.password)
        print(f"     Senha válida: {is_valid}")
        
    except User.DoesNotExist:
        print(f"   ❌ Usuário não encontrado no banco!")

print("\n=== CONFIGURAÇÕES ===")
from django.conf import settings
print(f"AUTH_USER_MODEL: {getattr(settings, 'AUTH_USER_MODEL', 'Not set')}")
print(f"AUTHENTICATION_BACKENDS: {getattr(settings, 'AUTHENTICATION_BACKENDS', 'Not set')}")
