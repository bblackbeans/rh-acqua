#!/usr/bin/env python3
"""
Script para debugar validação do formulário de vaga
Execute: python3 debug_validacao_formulario.py
"""

import requests
import json

def debug_form_validation():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🔍 DEBUG DE VALIDAÇÃO DO FORMULÁRIO DE VAGA")
    print("=" * 50)
    
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
    
    # 2. Acessar formulário de criação de vaga
    print("\n2. Acessando formulário de criação de vaga...")
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
    
    # 3. Testar POST com dados mínimos para ver erros de validação
    print("\n3. Testando POST com dados mínimos...")
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
            'Referer': f"{base_url}/vacancies/vacancy/create/",
            'X-CSRFToken': csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/vacancy/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200")
            
            # Verificar se há erros de validação na resposta
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("⚠️ Possível erro de validação no formulário")
                
                # Procurar por mensagens de erro específicas
                if 'field' in response.text.lower():
                    print("🔍 Encontrou referência a 'field' - possível erro de campo")
                if 'required' in response.text.lower():
                    print("🔍 Encontrou referência a 'required' - campo obrigatório")
                if 'invalid' in response.text.lower():
                    print("🔍 Encontrou referência a 'invalid' - valor inválido")
                    
        elif response.status_code == 302:
            print("✅ POST retornou 302 (redirecionamento - provavelmente sucesso)")
        elif response.status_code == 403:
            print("❌ Erro 403 - Problema de CSRF ou permissão")
        elif response.status_code == 400:
            print("⚠️ Erro 400 - Problema de validação de dados")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
        # Mostrar parte da resposta para análise
        print(f"\nResposta (primeiros 1000 caracteres):")
        print(response.text[:1000])
        
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Debug concluído!")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique se há mensagens de erro específicas na resposta")
    print("2. Teste com dados reais de hospitais e departamentos existentes")
    print("3. Verifique se todos os campos obrigatórios estão preenchidos")

if __name__ == "__main__":
    debug_form_validation()


