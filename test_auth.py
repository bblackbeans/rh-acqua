#!/usr/bin/env python3
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()

print("=== TESTE DETALHADO DE AUTENTICAÇÃO ===")

# Buscar usuários específicos que vimos no admin
test_emails = ['bea@gmail.com', 'kaue.ronald@gmail.com']

for email in test_emails:
    print(f"\n--- Testando usuário: {email} ---")
    
    try:
        user = User.objects.get(email=email)
        print(f"✅ Usuário encontrado no banco")
        print(f"   Nome: {user.get_full_name()}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Role: {user.role}")
        print(f"   Senha definida: {bool(user.password)}")
        print(f"   Hash da senha: {user.password[:50]}...")
        
        # Testar diferentes senhas comuns
        test_passwords = ['admin123', '123456', 'password', 'senha123', '123', '']
        
        for password in test_passwords:
            print(f"\n   Testando senha: '{password}'")
            
            # Teste 1: authenticate()
            auth_user = authenticate(username=email, password=password)
            if auth_user:
                print(f"   ✅ authenticate() funcionou!")
            else:
                print(f"   ❌ authenticate() falhou")
            
            # Teste 2: check_password()
            if user.password:
                is_valid = check_password(password, user.password)
                print(f"   {'✅' if is_valid else '❌'} check_password(): {is_valid}")
            else:
                print(f"   ❌ Usuário não tem senha definida")
        
    except User.DoesNotExist:
        print(f"❌ Usuário {email} não encontrado no banco")

print("\n=== TESTE DE CRIAÇÃO DE USUÁRIO ===")
# Testar criação de um usuário de teste
try:
    test_user = User.objects.create_user(
        email='teste@teste.com',
        password='123456',
        first_name='Teste',
        last_name='Usuario'
    )
    print(f"✅ Usuário de teste criado: {test_user.email}")
    
    # Testar autenticação do usuário recém-criado
    auth_user = authenticate(username='teste@teste.com', password='123456')
    if auth_user:
        print(f"✅ Autenticação do usuário recém-criado funcionou!")
    else:
        print(f"❌ Autenticação do usuário recém-criado falhou")
    
    # Limpar usuário de teste
    test_user.delete()
    print(f"✅ Usuário de teste removido")
    
except Exception as e:
    print(f"❌ Erro ao criar usuário de teste: {e}")

