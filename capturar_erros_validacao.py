#!/usr/bin/env python3
"""
Script para capturar erros específicos de validação do formulário
Execute: python3 capturar_erros_validacao.py
"""

import requests
import re
from bs4 import BeautifulSoup

def capture_validation_errors():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🔍 CAPTURANDO ERROS DE VALIDAÇÃO DO FORMULÁRIO")
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
    
    # 3. Testar POST e capturar erros
    print("\n3. Testando POST e capturando erros...")
    try:
        # Dados válidos baseados no banco
        data = {
            'csrfmiddlewaretoken': form_csrf_token,
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
            'X-CSRFToken': form_csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/vacancy/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200 - analisando erros...")
            
            # Usar BeautifulSoup para parsear HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Procurar por mensagens de erro
            print("\n🔍 PROCURANDO ERROS DE VALIDAÇÃO:")
            print("=" * 40)
            
            # 1. Procurar por divs com classe de erro
            error_divs = soup.find_all('div', class_=re.compile(r'error|invalid|alert'))
            if error_divs:
                print("📋 Divs com classe de erro encontradas:")
                for i, div in enumerate(error_divs[:5]):  # Limitar a 5
                    print(f"  {i+1}. {div.get_text().strip()}")
            
            # 2. Procurar por campos com classe is-invalid
            invalid_fields = soup.find_all(class_='is-invalid')
            if invalid_fields:
                print("\n📋 Campos com classe is-invalid:")
                for i, field in enumerate(invalid_fields[:5]):
                    print(f"  {i+1}. {field.get('name', 'Sem nome')}: {field.get('id', 'Sem ID')}")
            
            # 3. Procurar por mensagens de erro específicas
            error_messages = soup.find_all(text=re.compile(r'error|invalid|required|obrigatório', re.I))
            if error_messages:
                print("\n📋 Mensagens de erro encontradas:")
                unique_errors = set()
                for msg in error_messages:
                    clean_msg = msg.strip()
                    if clean_msg and len(clean_msg) > 3 and clean_msg not in unique_errors:
                        unique_errors.add(clean_msg)
                        print(f"  • {clean_msg}")
            
            # 4. Procurar por spans com classe de erro
            error_spans = soup.find_all('span', class_=re.compile(r'error|invalid'))
            if error_spans:
                print("\n📋 Spans com classe de erro:")
                for i, span in enumerate(error_spans[:5]):
                    print(f"  {i+1}. {span.get_text().strip()}")
            
            # 5. Procurar por campos obrigatórios não preenchidos
            required_fields = soup.find_all(attrs={'required': True})
            if required_fields:
                print(f"\n📋 Campos obrigatórios encontrados: {len(required_fields)}")
                for i, field in enumerate(required_fields[:5]):
                    print(f"  {i+1}. {field.get('name', 'Sem nome')}: {field.get('id', 'Sem ID')}")
            
            # 6. Procurar por mensagens específicas do Django
            django_errors = soup.find_all(text=re.compile(r'This field is required|Este campo é obrigatório|Invalid', re.I))
            if django_errors:
                print("\n📋 Erros específicos do Django:")
                for i, error in enumerate(django_errors[:5]):
                    print(f"  {i+1}. {error.strip()}")
            
            # 7. Verificar se há formulário com erros
            form_errors = soup.find_all('form')
            if form_errors:
                print(f"\n📋 Formulários encontrados: {len(form_errors)}")
                for i, form in enumerate(form_errors):
                    if 'error' in str(form).lower() or 'invalid' in str(form).lower():
                        print(f"  Formulário {i+1} contém erros")
            
            # 8. Salvar HTML completo para análise
            with open('formulario_com_erros.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n💾 HTML salvo em: formulario_com_erros.html")
            
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Análise concluída!")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique os erros específicos encontrados acima")
    print("2. Abra o arquivo formulario_com_erros.html no navegador")
    print("3. Identifique quais campos estão com erro")

if __name__ == "__main__":
    capture_validation_errors()


