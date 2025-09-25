#!/usr/bin/env python3
"""
Script para verificar as permissões dos usuários e corrigir roles se necessário.
Este script ajuda a diagnosticar problemas de autenticação e permissões.
"""

import os
import sys
import django

# Configurar o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from users.models import User

def check_users():
    """Verifica todos os usuários e suas permissões."""
    print("=" * 60)
    print("VERIFICAÇÃO DE USUÁRIOS E PERMISSÕES")
    print("=" * 60)
    
    users = User.objects.all()
    
    if not users.exists():
        print("❌ Nenhum usuário encontrado no sistema!")
        return
    
    print(f"Total de usuários: {users.count()}\n")
    
    for user in users:
        print(f"👤 USUÁRIO: {user.get_full_name()}")
        print(f"   📧 Email: {user.email}")
        print(f"   🔑 Role: {user.role} ({user.get_role_display()})")
        print(f"   ✅ Ativo: {'Sim' if user.is_active else 'Não'}")
        print(f"   👔 Staff: {'Sim' if user.is_staff else 'Não'}")
        print(f"   🔐 Superuser: {'Sim' if user.is_superuser else 'Não'}")
        print(f"   📅 Último login: {user.last_login}")
        
        # Verificar permissões específicas
        can_create_vacancy = user.role in ['recruiter', 'admin'] or user.is_superuser
        print(f"   📝 Pode criar vagas: {'✅ Sim' if can_create_vacancy else '❌ Não'}")
        
        # Verificar propriedades do modelo
        print(f"   🏥 É recrutador: {'Sim' if user.is_recruiter else 'Não'}")
        print(f"   👑 É admin: {'Sim' if user.is_admin else 'Não'}")
        print(f"   👨‍💼 É candidato: {'Sim' if user.is_candidate else 'Não'}")
        
        print("-" * 60)

def fix_user_permissions():
    """Corrige permissões de usuários que deveriam ter acesso."""
    print("\n" + "=" * 60)
    print("CORREÇÃO DE PERMISSÕES")
    print("=" * 60)
    
    print("Verificando usuários que precisam de ajuste...")
    
    # Buscar usuários que são staff ou superuser mas não têm role admin
    staff_users = User.objects.filter(is_staff=True, role='candidate')
    super_users = User.objects.filter(is_superuser=True, role='candidate')
    
    users_to_fix = []
    
    for user in staff_users:
        users_to_fix.append((user, 'admin', 'usuário staff'))
    
    for user in super_users:
        users_to_fix.append((user, 'admin', 'superusuário'))
    
    if not users_to_fix:
        print("✅ Todos os usuários têm permissões corretas!")
        return
    
    print(f"Encontrados {len(users_to_fix)} usuários para corrigir:")
    
    for user, new_role, reason in users_to_fix:
        print(f"\n👤 {user.get_full_name()} ({user.email})")
        print(f"   Reason: {reason}")
        print(f"   Role atual: {user.role}")
        print(f"   Novo role: {new_role}")
        
        # Aplicar correção
        user.role = new_role
        user.save()
        
        print(f"   ✅ Corrigido!")

def create_test_users():
    """Cria usuários de teste se não existirem."""
    print("\n" + "=" * 60)
    print("CRIAÇÃO DE USUÁRIOS DE TESTE")
    print("=" * 60)
    
    # Verificar se já existe um admin
    admin_users = User.objects.filter(role='admin')
    recruiter_users = User.objects.filter(role='recruiter')
    
    if not admin_users.exists():
        print("Criando usuário ADMIN...")
        try:
            admin = User.objects.create_user(
                email='admin@rhacqua.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            print(f"✅ Admin criado: {admin.email}")
        except Exception as e:
            print(f"❌ Erro ao criar admin: {e}")
    else:
        print(f"✅ Já existe {admin_users.count()} admin(s)")
    
    if not recruiter_users.exists():
        print("Criando usuário RECRUTADOR...")
        try:
            recruiter = User.objects.create_user(
                email='recruiter@rhacqua.com',
                password='admin123',
                first_name='Maria',
                last_name='Recrutadora',
                role='recruiter',
                is_staff=True
            )
            print(f"✅ Recrutador criado: {recruiter.email}")
        except Exception as e:
            print(f"❌ Erro ao criar recrutador: {e}")
    else:
        print(f"✅ Já existe {recruiter_users.count()} recrutador(es)")

def main():
    """Função principal do script."""
    print("🔍 DIAGNÓSTICO DE USUÁRIOS E PERMISSÕES")
    print("Este script verifica e corrige problemas de permissões de usuário.\n")
    
    try:
        # Verificar usuários existentes
        check_users()
        
        # Corrigir permissões se necessário
        fix_user_permissions()
        
        # Criar usuários de teste se necessário
        create_test_users()
        
        print("\n" + "=" * 60)
        print("RESUMO FINAL")
        print("=" * 60)
        
        total_users = User.objects.count()
        admin_count = User.objects.filter(role='admin').count()
        recruiter_count = User.objects.filter(role='recruiter').count()
        candidate_count = User.objects.filter(role='candidate').count()
        
        print(f"Total de usuários: {total_users}")
        print(f"Administradores: {admin_count}")
        print(f"Recrutadores: {recruiter_count}")
        print(f"Candidatos: {candidate_count}")
        
        if admin_count > 0 or recruiter_count > 0:
            print("\n✅ Há usuários com permissão para criar vagas!")
            print("\n🔗 CREDENCIAIS PARA TESTE:")
            
            if admin_count > 0:
                admin = User.objects.filter(role='admin').first()
                print(f"ADMIN: {admin.email} / admin123")
            
            if recruiter_count > 0:
                recruiter = User.objects.filter(role='recruiter').first()
                print(f"RECRUTADOR: {recruiter.email} / admin123")
        else:
            print("\n⚠️ Nenhum usuário com permissão para criar vagas!")
        
        print(f"\n📍 URL para criar vaga: /vacancies/vacancy/create/")
        
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
