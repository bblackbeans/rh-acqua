#!/usr/bin/env python3
"""
Script para debug detalhado do formulário de vaga
Execute: python3 debug_formulario_detalhado.py
"""

import requests
import re
from bs4 import BeautifulSoup

def debug_form_detailed():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🔍 DEBUG DETALHADO DO FORMULÁRIO DE VAGA")
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
    
    # 3. Testar POST com dados mínimos e válidos
    print("\n3. Testando POST com dados válidos...")
    try:
        # Dados válidos baseados no banco
        data = {
            'csrfmiddlewaretoken': form_csrf_token,
            'title': 'Vaga de Teste Debug',
            'description': 'Descrição de teste para debug',
            'requirements': 'Requisitos de teste para debug',
            'hospital': '1',  # Hospital Municipal Materno Infantil da Serra
            'department': '3',  # Administração
            'location': 'São Paulo, SP',
            'contract_type': 'full_time',  # Valor correto
            'experience_level': 'junior',  # Valor correto
            'is_remote': 'false',
            'is_salary_visible': 'false',  # Simplificar
            'status': 'draft'
        }
        
        headers = {
            'Referer': f"{base_url}/vacancies/vacancy/create/",
            'X-CSRFToken': form_csrf_token
        }
        
        response = session.post(f"{base_url}/vacancies/vacancy/create/", data=data, headers=headers)
        print(f"Status do POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST retornou 200 - analisando resposta...")
            
            # Salvar resposta completa
            with open('formulario_resposta_completa.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Resposta salva em: formulario_resposta_completa.html")
            
            # Usar BeautifulSoup para análise detalhada
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("\n🔍 ANÁLISE DETALHADA DOS ERROS:")
            print("=" * 40)
            
            # 1. Procurar por todos os campos com classe is-invalid
            invalid_fields = soup.find_all(class_='is-invalid')
            if invalid_fields:
                print(f"📋 Campos com classe is-invalid ({len(invalid_fields)}):")
                for i, field in enumerate(invalid_fields):
                    field_name = field.get('name', 'Sem nome')
                    field_id = field.get('id', 'Sem ID')
                    field_type = field.get('type', 'Sem tipo')
                    print(f"  {i+1}. Nome: {field_name}, ID: {field_id}, Tipo: {field_type}")
            
            # 2. Procurar por divs com mensagens de erro
            error_divs = soup.find_all('div', class_=re.compile(r'invalid-feedback|error|alert'))
            if error_divs:
                print(f"\n📋 Divs com mensagens de erro ({len(error_divs)}):")
                for i, div in enumerate(error_divs):
                    error_text = div.get_text().strip()
                    if error_text:
                        print(f"  {i+1}. {error_text}")
            
            # 3. Procurar por spans com mensagens de erro
            error_spans = soup.find_all('span', class_=re.compile(r'error|invalid'))
            if error_spans:
                print(f"\n📋 Spans com mensagens de erro ({len(error_spans)}):")
                for i, span in enumerate(error_spans):
                    error_text = span.get_text().strip()
                    if error_text:
                        print(f"  {i+1}. {error_text}")
            
            # 4. Procurar por campos obrigatórios não preenchidos
            required_fields = soup.find_all(attrs={'required': True})
            if required_fields:
                print(f"\n📋 Campos obrigatórios encontrados ({len(required_fields)}):")
                for i, field in enumerate(required_fields):
                    field_name = field.get('name', 'Sem nome')
                    field_id = field.get('id', 'Sem ID')
                    field_value = field.get('value', '')
                    print(f"  {i+1}. Nome: {field_name}, ID: {field_id}, Valor: '{field_value}'")
            
            # 5. Procurar por mensagens específicas do Django
            django_errors = soup.find_all(text=re.compile(r'This field is required|Este campo é obrigatório|Invalid|Required', re.I))
            if django_errors:
                print(f"\n📋 Mensagens específicas do Django ({len(django_errors)}):")
                unique_errors = set()
                for error in django_errors:
                    clean_error = error.strip()
                    if clean_error and len(clean_error) > 3 and clean_error not in unique_errors:
                        unique_errors.add(clean_error)
                        print(f"  • {clean_error}")
            
            # 6. Verificar se há JavaScript de validação
            scripts = soup.find_all('script')
            validation_scripts = [script for script in scripts if script.string and ('validation' in script.string.lower() or 'error' in script.string.lower())]
            if validation_scripts:
                print(f"\n📋 Scripts de validação encontrados ({len(validation_scripts)}):")
                for i, script in enumerate(validation_scripts):
                    print(f"  {i+1}. Script contém validação")
            
            # 7. Verificar se o formulário foi redirecionado
            if 'login' in response.text.lower() and 'password' in response.text.lower():
                print("\n⚠️ ATENÇÃO: A resposta contém página de login - sessão pode ter expirado")
            
            # 8. Verificar se há mensagens de sucesso
            if 'sucesso' in response.text.lower() or 'success' in response.text.lower():
                print("\n✅ Possível mensagem de sucesso encontrada na resposta")
            
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no POST: {e}")
    
    print("\n✅ Debug detalhado concluído!")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique os erros específicos encontrados acima")
    print("2. Abra o arquivo formulario_resposta_completa.html no navegador")
    print("3. Procure por campos destacados em vermelho")
    print("4. Verifique se há mensagens de erro específicas")

if __name__ == "__main__":
    debug_form_detailed()


