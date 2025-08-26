#!/usr/bin/env python
"""
Script para migrar dados do SQLite para PostgreSQL
Execute este script antes de usar o PostgreSQL
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

def migrate_data():
    """Migra dados do SQLite para PostgreSQL"""
    print("🔄 Iniciando migração de dados...")
    
    # 1. Fazer backup dos dados atuais
    print("📦 Fazendo backup dos dados atuais...")
    execute_from_command_line(['manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', '-e', 'contenttypes', '-e', 'auth.Permission', '-o', 'backup_data.json'])
    
    # 2. Criar migrações para PostgreSQL
    print("🔧 Criando migrações...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # 3. Aplicar migrações
    print("📊 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # 4. Carregar dados do backup
    print("📥 Carregando dados do backup...")
    execute_from_command_line(['manage.py', 'loaddata', 'backup_data.json'])
    
    print("✅ Migração concluída com sucesso!")
    print("📁 Backup salvo em: backup_data.json")

if __name__ == '__main__':
    migrate_data()
