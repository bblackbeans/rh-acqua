#!/usr/bin/env python3
"""
Script para deletar a vaga "Teste FK Corrigido" do banco de dados
"""

import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from vacancies.models import Vacancy

def delete_vaga_teste():
    """Deleta a vaga 'Teste FK Corrigido' do banco"""
    try:
        # Procura pela vaga com o título específico
        vaga = Vacancy.objects.filter(title__icontains='Teste FK Corrigido').first()
        
        if vaga:
            print(f"Vaga encontrada: {vaga.title} (ID: {vaga.pk})")
            print(f"Status: {vaga.status}")
            print(f"Recrutador: {vaga.recruiter}")
            
            # Verifica se tem candidaturas
            if vaga.applications.exists():
                print(f"⚠️  ATENÇÃO: Esta vaga possui {vaga.applications.count()} candidatura(s)")
                response = input("Deseja continuar mesmo assim? (s/N): ")
                if response.lower() != 's':
                    print("Operação cancelada.")
                    return
            
            # Confirma a exclusão
            response = input(f"Tem certeza que deseja excluir a vaga '{vaga.title}'? (s/N): ")
            if response.lower() == 's':
                vaga.delete()
                print("✅ Vaga excluída com sucesso!")
            else:
                print("Operação cancelada.")
        else:
            print("❌ Nenhuma vaga com 'Teste FK Corrigido' encontrada.")
            
            # Lista todas as vagas para ajudar na identificação
            print("\n📋 Vagas disponíveis:")
            vagas = Vacancy.objects.all().order_by('title')
            for v in vagas:
                print(f"  - {v.title} (ID: {v.pk}, Status: {v.status})")
                
    except Exception as e:
        print(f"❌ Erro ao deletar a vaga: {e}")

if __name__ == "__main__":
    delete_vaga_teste() 