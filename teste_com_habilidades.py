#!/usr/bin/env python3
"""
Script para testar criação de vaga com habilidades
Execute: python3 teste_com_habilidades.py
"""

import requests
import re

def test_vacancy_with_skills():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🔐 TESTE DE CRIAÇÃO DE VAGA COM HABILIDADES")
    print("=" * 50)
    
    session = requests.Session()
    
    # 1. Login
    print("1. Fazendo login...")
    try:
        login_page = session.get(f"{base_url}/users/login/")
        csrf_token = None
        for line in login_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'rosana@institutoacqua.org.br',
            'password': 'UDgEMcLud882xyM',
        }
        
        headers = {
            'Referer': f"{base_url}/users/login/",
            'X-CSRFToken': csrf_token
        }
        
        login_response = session.post(f"{base_url}/users/login/", data=login_data, headers=headers)
        print(f"Status do login: {login_response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return
    
    # 2. Acessar formulário
    print("\n2. Acessando formulário...")
    try:
        form_page = session.get(f"{base_url}/vacancies/vacancy/create/")
        form_csrf_token = None
        for line in form_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                form_csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        print(f"Status do formulário: {form_page.status_code}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar formulário: {e}")
        return
    
    # 3. Testar POST com dados válidos + habilidades
    print("\n3. Testando POST com dados válidos + habilidades...")
    try:
        # Dados válidos baseados no banco + habilidades
        data = {
            'csrfmiddlewaretoken': form_csrf_token,
            'title': 'Vaga de Teste Debug',
            'description': 'Descrição de teste para debug',
            'requirements': 'Requisitos de teste para debug',
            'hospital': '1',  # Hospital Municipal Materno Infantil da Serra
            'department': '3',  # Administração
            'location': 'São Paulo, SP',
            'contract_type': 'full_time',
            'experience_level': 'junior',
            'is_remote': 'false',
            'is_salary_visible': 'false',
            'status': 'draft',
            'skills': '1'  # Adicionar pelo menos uma habilidade
        }
        
        headers = {
            'Referer': f"{base_url}/vacancies/vacancy/create/",
            'X-CSRFToken': form_csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/vacancy/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200")
            
            # Verificar se há erros de validação
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("⚠️ Ainda há erros de validação")
                
                # Procurar por mensagens específicas
                if 'habilidade' in response.text.lower():
                    print("🔍 Erro relacionado a habilidades")
                if 'departamento' in response.text.lower():
                    print("🔍 Erro relacionado a departamento")
                if 'hospital' in response.text.lower():
                    print("🔍 Erro relacionado a hospital")
                    
            else:
                print("✅ Possível sucesso - sem erros de validação")
                
        elif response.status_code == 302:
            print("✅ POST retornou 302 (redirecionamento - provavelmente sucesso)")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
        # Mostrar parte da resposta
        print(f"\nResposta (primeiros 500 caracteres):")
        print(response.text[:500])
        
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Teste concluído!")
    print("\n🎯 PROBLEMAS IDENTIFICADOS:")
    print("1. ❌ Habilidades são obrigatórias (pelo menos uma)")
    print("2. ❌ Departamento deve pertencer ao hospital selecionado")
    print("3. ❌ Validações de salário e datas")
    print("\n🎯 SOLUÇÃO:")
    print("1. Selecione pelo menos uma habilidade no formulário")
    print("2. Verifique se o departamento pertence ao hospital")
    print("3. Preencha todos os campos obrigatórios corretamente")

if __name__ == "__main__":
    test_vacancy_with_skills()


