#!/bin/bash

echo "🔍 DEBUG DE CAMPO ESPECÍFICO COM ERRO"
echo "===================================="

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
echo "3️⃣ TESTANDO POST E CAPTURANDO ERROS ESPECÍFICOS"
echo "=============================================="

# Fazer POST com dados válidos
echo "Enviando dados do formulário..."
post_response=$(curl -s -b cookies.txt \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: $base_url/vacancies/vacancy/create/" \
  -d "csrfmiddlewaretoken=$csrf_token&title=Vaga de Teste Debug&description=Descrição de teste&requirements=Requisitos de teste&hospital=1&department=3&location=São Paulo, SP&contract_type=full_time&experience_level=junior&is_remote=false&is_salary_visible=false&status=draft&skills=1" \
  "$base_url/vacancies/vacancy/create/")

echo "✅ POST enviado"

echo ""
echo "4️⃣ ANALISANDO ERROS ESPECÍFICOS"
echo "=============================="

# Salvar resposta em arquivo
echo "$post_response" > formulario_erro_detalhado.html

# Procurar por erros específicos
echo "🔍 Procurando erros específicos..."

# 1. Procurar por campos com classe is-invalid
echo ""
echo "📋 Campos com classe is-invalid:"
echo "$post_response" | grep -o 'class="[^"]*is-invalid[^"]*"' | head -10

# 2. Procurar por mensagens de erro específicas
echo ""
echo "📋 Mensagens de erro encontradas:"
echo "$post_response" | grep -i "error\|invalid\|required\|obrigatório" | head -10

# 3. Procurar por divs com classe invalid-feedback
echo ""
echo "📋 Divs com classe invalid-feedback:"
echo "$post_response" | grep -o '<div[^>]*class="[^"]*invalid-feedback[^"]*"[^>]*>[^<]*</div>' | head -5

# 4. Procurar por campos específicos com erro
echo ""
echo "📋 Campos específicos com erro:"
echo "$post_response" | grep -o 'name="[^"]*"[^>]*class="[^"]*is-invalid[^"]*"' | head -10

# 5. Procurar por mensagens de validação do Django
echo ""
echo "📋 Mensagens de validação do Django:"
echo "$post_response" | grep -i "this field is required\|este campo é obrigatório\|invalid\|validation" | head -10

# 6. Procurar por campos obrigatórios não preenchidos
echo ""
echo "📋 Campos obrigatórios não preenchidos:"
echo "$post_response" | grep -o 'required[^>]*' | head -10

# 7. Verificar se há JavaScript de validação
echo ""
echo "📋 JavaScript de validação:"
echo "$post_response" | grep -i "validation\|error\|invalid" | grep -i "script" | head -5

echo ""
echo "5️⃣ VERIFICANDO CAMPOS ESPECÍFICOS"
echo "================================="

# Verificar campos específicos que podem estar causando erro
echo "🔍 Verificando campos específicos..."

# Verificar se há erro no campo hospital
if echo "$post_response" | grep -q "hospital.*error\|hospital.*invalid"; then
    echo "❌ Erro no campo hospital"
fi

# Verificar se há erro no campo department
if echo "$post_response" | grep -q "department.*error\|department.*invalid"; then
    echo "❌ Erro no campo department"
fi

# Verificar se há erro no campo skills
if echo "$post_response" | grep -q "skills.*error\|skills.*invalid"; then
    echo "❌ Erro no campo skills"
fi

# Verificar se há erro no campo title
if echo "$post_response" | grep -q "title.*error\|title.*invalid"; then
    echo "❌ Erro no campo title"
fi

# Verificar se há erro no campo location
if echo "$post_response" | grep -q "location.*error\|location.*invalid"; then
    echo "❌ Erro no campo location"
fi

echo ""
echo "✅ Análise concluída!"
echo ""
echo "💾 Resposta completa salva em: formulario_erro_detalhado.html"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Verifique os erros específicos encontrados acima"
echo "2. Abra o arquivo formulario_erro_detalhado.html no navegador"
echo "3. Procure por campos destacados em vermelho"
echo "4. Identifique qual campo específico está causando o erro"

# Limpar cookies
rm -f cookies.txt


