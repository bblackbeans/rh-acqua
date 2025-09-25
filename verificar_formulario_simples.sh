#!/bin/bash

echo "🔍 VERIFICAÇÃO SIMPLES DO FORMULÁRIO"
echo "==================================="

base_url="https://rh.institutoacqua.org.br"

echo ""
echo "1️⃣ TESTANDO ACESSO AO FORMULÁRIO"
echo "==============================="

# Testar se o formulário está acessível
echo "Testando acesso ao formulário..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$base_url/vacancies/vacancy/create/")
echo "Status: $response"

if [ "$response" = "200" ]; then
    echo "✅ Formulário acessível"
elif [ "$response" = "302" ]; then
    echo "⚠️ Redirecionamento (provavelmente para login)"
else
    echo "❌ Erro: $response"
fi

echo ""
echo "2️⃣ VERIFICANDO CAMPOS OBRIGATÓRIOS NO CÓDIGO"
echo "============================================"

# Verificar se há validações específicas no formulário
echo "Procurando validações no código do formulário..."

if [ -f "vacancies/forms.py" ]; then
    echo "📋 Campos obrigatórios no VacancyForm:"
    grep -n "required=True" vacancies/forms.py | head -10
    
    echo ""
    echo "📋 Validações customizadas:"
    grep -n "def clean_" vacancies/forms.py | head -5
    
    echo ""
    echo "📋 Campos com validação especial:"
    grep -n "validators\|validation" vacancies/forms.py | head -5
else
    echo "❌ Arquivo vacancies/forms.py não encontrado"
fi

echo ""
echo "3️⃣ VERIFICANDO MODELO VACANCY"
echo "============================="

if [ -f "vacancies/models.py" ]; then
    echo "📋 Campos obrigatórios no modelo Vacancy:"
    grep -A 2 -B 2 "CharField\|TextField" vacancies/models.py | grep -v "blank=True\|null=True" | head -10
else
    echo "❌ Arquivo vacancies/models.py não encontrado"
fi

echo ""
echo "4️⃣ VERIFICANDO VIEWS DE CRIAÇÃO"
echo "==============================="

if [ -f "vacancies/views.py" ]; then
    echo "📋 VacancyCreateView:"
    grep -A 10 -B 5 "class VacancyCreateView" vacancies/views.py
    
    echo ""
    echo "📋 form_valid method:"
    grep -A 20 "def form_valid" vacancies/views.py | head -25
else
    echo "❌ Arquivo vacancies/views.py não encontrado"
fi

echo ""
echo "5️⃣ POSSÍVEIS CAUSAS DO ERRO"
echo "==========================="

echo "🔍 Baseado na análise, as possíveis causas são:"
echo ""
echo "1. ❌ Validação customizada no formulário"
echo "2. ❌ Campo obrigatório não mapeado no formulário"
echo "3. ❌ Validação de relacionamento (hospital-departamento)"
echo "4. ❌ Validação de permissão do usuário"
echo "5. ❌ Validação de dados específicos (formato, tamanho, etc.)"
echo "6. ❌ Validação JavaScript no frontend"
echo "7. ❌ Validação de integridade do banco de dados"

echo ""
echo "6️⃣ COMANDOS PARA DEBUG MAIS PROFUNDO"
echo "===================================="

echo "Execute estes comandos para investigar mais:"
echo ""
echo "# Ver logs do Django em tempo real"
echo "sudo docker logs -f rh-acqua-web-1"
echo ""
echo "# Verificar se há erros específicos no banco"
echo "sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c \"SELECT * FROM django_migrations WHERE app = 'vacancies';\""
echo ""
echo "# Verificar se há constraints no banco"
echo "sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c \"\\d vacancies_vacancy\""

echo ""
echo "✅ Verificação concluída!"


