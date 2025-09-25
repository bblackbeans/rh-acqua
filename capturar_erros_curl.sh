#!/bin/bash

echo "🔍 CAPTURANDO ERROS DE VALIDAÇÃO COM CURL"
echo "========================================="

base_url="https://rh.institutoacqua.org.br"

echo ""
echo "1️⃣ FAZENDO LOGIN E OBTENDO COOKIES"
echo "=================================="

# Fazer login e salvar cookies
echo "Fazendo login..."
curl -s -c cookies.txt -b cookies.txt \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: $base_url/users/login/" \
  -d "username=rosana@institutoacqua.org.br&password=UDgEMcLud882xyM" \
  "$base_url/users/login/" > /dev/null

echo "✅ Login realizado"

echo ""
echo "2️⃣ OBTENDO FORMULÁRIO E CSRF TOKEN"
echo "=================================="

# Obter formulário e CSRF token
echo "Obtendo formulário..."
form_response=$(curl -s -b cookies.txt "$base_url/vacancies/vacancy/create/")

# Extrair CSRF token
csrf_token=$(echo "$form_response" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | sed 's/name="csrfmiddlewaretoken" value="\([^"]*\)"/\1/')

if [ ! -z "$csrf_token" ]; then
    echo "✅ CSRF token obtido: ${csrf_token:0:20}..."
else
    echo "❌ CSRF token não encontrado"
    exit 1
fi

echo ""
echo "3️⃣ TESTANDO POST E CAPTURANDO ERROS"
echo "==================================="

# Fazer POST com dados válidos
echo "Enviando dados do formulário..."
post_response=$(curl -s -b cookies.txt \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: $base_url/vacancies/vacancy/create/" \
  -d "csrfmiddlewaretoken=$csrf_token&title=Vaga de Teste Debug&description=Descrição de teste&requirements=Requisitos de teste&hospital=1&department=3&location=Local de teste&contract_type=clt&experience_level=junior&is_remote=false&is_salary_visible=true&min_salary=1000&max_salary=2000&category=1&benefits=Benefícios de teste&status=draft" \
  "$base_url/vacancies/vacancy/create/")

echo "✅ POST enviado"

echo ""
echo "4️⃣ ANALISANDO ERROS DE VALIDAÇÃO"
echo "==============================="

# Salvar resposta em arquivo
echo "$post_response" > formulario_resposta.html

# Procurar por erros específicos
echo "🔍 Procurando erros de validação..."

# 1. Procurar por campos com classe is-invalid
echo ""
echo "📋 Campos com classe is-invalid:"
echo "$post_response" | grep -o 'class="[^"]*is-invalid[^"]*"' | head -10

# 2. Procurar por mensagens de erro
echo ""
echo "📋 Mensagens de erro encontradas:"
echo "$post_response" | grep -i "error\|invalid\|required\|obrigatório" | head -10

# 3. Procurar por divs com classe de erro
echo ""
echo "📋 Divs com classe de erro:"
echo "$post_response" | grep -o '<div[^>]*class="[^"]*error[^"]*"[^>]*>[^<]*</div>' | head -5

# 4. Procurar por spans com classe de erro
echo ""
echo "📋 Spans com classe de erro:"
echo "$post_response" | grep -o '<span[^>]*class="[^"]*error[^"]*"[^>]*>[^<]*</span>' | head -5

# 5. Procurar por campos obrigatórios
echo ""
echo "📋 Campos obrigatórios encontrados:"
echo "$post_response" | grep -o 'required[^>]*' | head -10

# 6. Procurar por mensagens específicas do Django
echo ""
echo "📋 Mensagens específicas do Django:"
echo "$post_response" | grep -i "this field is required\|este campo é obrigatório\|invalid" | head -5

echo ""
echo "✅ Análise concluída!"
echo ""
echo "💾 Resposta completa salva em: formulario_resposta.html"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Verifique os erros específicos encontrados acima"
echo "2. Abra o arquivo formulario_resposta.html no navegador"
echo "3. Identifique quais campos estão com erro"

# Limpar cookies
rm -f cookies.txt


