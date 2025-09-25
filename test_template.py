#!/usr/bin/env python3
"""
Teste simples para verificar se o template está funcionando
"""

import os
import sys
import django
sys.path.insert(0, '/home/institutoacquaor/public_html/rh-acqua')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from vacancies.models import Vacancy
from django.template.loader import render_to_string
from django.http import HttpRequest

def test_template():
    """Testa se o template está renderizando corretamente"""
    try:
        vaga = Vacancy.objects.get(pk=91)
        print(f"✅ Vaga encontrada: {vaga.title}")
        print(f"✅ Salário visível: {vaga.is_salary_visible}")
        print(f"✅ Salário formatado: {vaga.formatted_salary_range}")
        
        # Simula um request
        request = HttpRequest()
        request.user = None
        
        # Contexto para o template
        context = {
            'vacancy': vaga,
            'active_applications': 0,
            'total_applications': 0,
            'related_vacancies': [],
            'is_public': True,
        }
        
        # Renderiza o template
        html = render_to_string('vacancies/public_vacancy_detail.html', context, request=request)
        
        # Verifica se o salário está no HTML
        if "R$ 3036.00" in html:
            print("✅ Salário encontrado no template renderizado!")
        else:
            print("❌ Salário NÃO encontrado no template")
            # Procura por outras variações
            if "salário" in html.lower():
                print("   Mas encontrou a palavra 'salário'")
            if "R$" in html:
                print("   Mas encontrou 'R$'")
        
        # Salva o HTML em um arquivo para análise
        with open('/tmp/template_test.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ Template salvo em /tmp/template_test.html para análise")
        
    except Exception as e:
        print(f"❌ Erro ao testar template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template()
