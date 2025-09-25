#!/usr/bin/env python3
"""
Script para testar criação de vaga com autenticação
Execute: python3 teste_com_autenticacao.py
"""

import requests
import json

def test_vacancy_with_auth():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🔐 TESTE DE CRIAÇÃO DE VAGA COM AUTENTICAÇÃO")
    print("=" * 50)
    
    session = requests.Session()
    
    # 1. Obter página de login
    print("1. Acessando página de login...")
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
    
    # 2. Fazer login (você precisa fornecer credenciais válidas)
    print("\n2. Fazendo login...")
    print("⚠️  IMPORTANTE: Você precisa fornecer credenciais de recrutador válidas")
    print("   Edite este script e adicione suas credenciais nas linhas abaixo:")
    print("   username = 'seu_usuario'")
    print("   password = 'sua_senha'")
    
    # Substitua pelas suas credenciais
    username = "rosana@institutoacqua.org.br"  # ALTERE AQUI
    password = "UDgEMcLud882xyM"  # ALTERE AQUI
    
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': username,
        'password': password,
    }
    
    headers = {
        'Referer': f"{base_url}/users/login/",
        'X-CSRFToken': csrf_token
    }
    
    try:
        login_response = session.post(f"{base_url}/users/login/", data=login_data, headers=headers)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login realizado")
        elif login_response.status_code == 302:
            print("✅ Login realizado (redirecionamento)")
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            print("Resposta do login:")
            print(login_response.text[:500])
            return
    
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return
    
    # 3. Acessar formulário de criação de vaga
    print("\n3. Acessando formulário de criação de vaga...")
    try:
        form_page = session.get(f"{base_url}/vacancies/vacancy/create/")
        print(f"Status do formulário: {form_page.status_code}")
        
        if form_page.status_code == 200:
            print("✅ Formulário acessível")
            
            # Extrair CSRF token do formulário
            form_csrf_token = None
            for line in form_page.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    form_csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if form_csrf_token:
                print(f"✅ CSRF token do formulário: {form_csrf_token[:20]}...")
                csrf_token = form_csrf_token
            else:
                print("❌ CSRF token não encontrado no formulário")
        elif form_page.status_code == 302:
            print("⚠️ Redirecionamento (provavelmente para login)")
            print(f"Location: {form_page.headers.get('Location', 'N/A')}")
            return
        else:
            print(f"❌ Erro ao acessar formulário: {form_page.status_code}")
            return
    
    except Exception as e:
        print(f"❌ Erro ao acessar formulário: {e}")
        return
    
    # 4. Testar POST com dados válidos do banco
    print("\n4. Testando POST com dados válidos...")
    try:
        # Dados válidos baseados no banco
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'title': 'Vaga de Teste Debug',
            'description': 'Descrição de teste para debug',
            'requirements': 'Requisitos de teste para debug',
            'hospital': '1',  # Hospital Municipal Materno Infantil da Serra
            'department': '3',  # Administração
            'location': 'Local de teste',
            'contract_type': 'clt',
            'experience_level': 'junior',
            'is_remote': 'false',
            'is_salary_visible': 'true',
            'min_salary': '1000',
            'max_salary': '2000',
            'category': '1',  # Teste
            'benefits': 'Benefícios de teste',
            'status': 'draft'
        }
        
        headers = {
            'Referer': f"{base_url}/vacancies/vacancy/create/",
            'X-CSRFToken': csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/vacancy/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200")
            
            # Verificar se há erros de validação
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("⚠️ Possível erro de validação no formulário")
                
                # Procurar por mensagens de erro específicas
                if 'field' in response.text.lower():
                    print("🔍 Encontrou referência a 'field' - possível erro de campo")
                if 'required' in response.text.lower():
                    print("🔍 Encontrou referência a 'required' - campo obrigatório")
                if 'invalid' in response.text.lower():
                    print("🔍 Encontrou referência a 'invalid' - valor inválido")
                    
            # Mostrar parte da resposta
            print(f"\nResposta (primeiros 1000 caracteres):")
            print(response.text[:1000])
                    
        elif response.status_code == 302:
            print("✅ POST retornou 302 (redirecionamento - provavelmente sucesso)")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 403:
            print("❌ Erro 403 - Problema de CSRF ou permissão")
        elif response.status_code == 400:
            print("⚠️ Erro 400 - Problema de validação de dados")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Teste concluído!")
    print("\n🎯 INSTRUÇÕES:")
    print("1. Edite este script e adicione suas credenciais de recrutador")
    print("2. Execute novamente: python3 teste_com_autenticacao.py")
    print("3. Verifique se o salvamento funciona com dados válidos")

if __name__ == "__main__":
    test_vacancy_with_auth()


