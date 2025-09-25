#!/usr/bin/env python3
"""
Script para testar a URL correta de criação de vaga
Execute: python3 teste_url_correta.py
"""

import requests
import json

def test_correct_vacancy_url():
    base_url = "https://rh.institutoacqua.org.br"
    
    print("🧪 TESTE COM URL CORRETA DE CRIAÇÃO DE VAGA")
    print("=" * 50)
    
    # 1. Testar URL correta
    print("1. Testando URL correta: /vacancies/vacancy/create/")
    try:
        response = requests.get(f"{base_url}/vacancies/vacancy/create/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ URL correta acessível!")
            
            # Verificar se tem CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if csrf_token:
                print(f"✅ CSRF token encontrado: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token não encontrado")
                
        elif response.status_code == 302:
            print("⚠️ Redirecionamento (provavelmente para login)")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 403:
            print("❌ Erro 403 - Problema de CSRF ou permissão")
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n2. Testando URL incorreta: /vacancies/create/")
    try:
        response = requests.get(f"{base_url}/vacancies/create/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Confirmado: URL incorreta retorna 404")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n3. Testando página de gestão de vagas")
    try:
        response = requests.get(f"{base_url}/vacancies/recruiter/gestao-vagas/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de gestão acessível")
        elif response.status_code == 302:
            print("⚠️ Redirecionamento (provavelmente para login)")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n✅ Teste concluído!")
    print("\n🎯 CONCLUSÃO:")
    print("A URL correta para criação de vaga é:")
    print("https://rh.institutoacqua.org.br/vacancies/vacancy/create/")

if __name__ == "__main__":
    test_correct_vacancy_url()
