#!/usr/bin/env python3
"""
Script para testar o salvamento de vagas via API
Execute: python3 teste_api_vagas.py
"""

import requests
import json

def test_vacancy_creation():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🧪 TESTE DE CRIAÇÃO DE VAGA VIA API")
    print("=" * 40)
    
    # 1. Obter página de login para pegar CSRF token
    print("1. Obtendo CSRF token...")
    session = requests.Session()
    
    try:
        login_page = session.get(f"{base_url}/users/login/")
        if login_page.status_code == 200:
            print("✅ Página de login acessível")
            
            # Extrair CSRF token
            csrf_token = None
            for line in login_page.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if csrf_token:
                print(f"✅ CSRF token obtido: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token não encontrado")
                return
        else:
            print(f"❌ Erro ao acessar página de login: {login_page.status_code}")
            return
    
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 2. Tentar acessar formulário de criação de vaga
    print("\n2. Testando acesso ao formulário de vaga...")
    try:
        form_page = session.get(f"{base_url}/vacancies/create/")
        print(f"Status do formulário: {form_page.status_code}")
        
        if form_page.status_code == 200:
            print("✅ Formulário de criação acessível")
        elif form_page.status_code == 302:
            print("⚠️ Redirecionamento (provavelmente para login)")
        else:
            print(f"❌ Erro ao acessar formulário: {form_page.status_code}")
    
    except Exception as e:
        print(f"❌ Erro ao acessar formulário: {e}")
    
    # 3. Testar POST com dados mínimos
    print("\n3. Testando envio de dados...")
    try:
        # Dados mínimos para teste
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'title': 'Vaga de Teste',
            'description': 'Descrição de teste',
            'requirements': 'Requisitos de teste',
            'hospital': '1',  # Assumindo que existe hospital com ID 1
            'department': '1',  # Assumindo que existe departamento com ID 1
            'location': 'Local de teste',
            'contract_type': 'clt',
            'experience_level': 'junior',
            'is_remote': 'false',
            'is_salary_visible': 'true',
            'min_salary': '1000',
            'max_salary': '2000'
        }
        
        headers = {
            'Referer': f"{base_url}/vacancies/create/",
            'X-CSRFToken': csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200 (pode ser formulário com erros)")
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("⚠️ Possível erro de validação no formulário")
        elif response.status_code == 302:
            print("✅ POST retornou 302 (redirecionamento - provavelmente sucesso)")
        elif response.status_code == 403:
            print("❌ Erro 403 - Problema de CSRF ou permissão")
        elif response.status_code == 400:
            print("⚠️ Erro 400 - Problema de validação de dados")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
        # Mostrar parte da resposta para análise
        print(f"\nResposta (primeiros 500 caracteres):")
        print(response.text[:500])
        
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_vacancy_creation()
