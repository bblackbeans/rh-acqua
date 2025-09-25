#!/bin/bash

echo "🔍 DIAGNÓSTICO DE SALVAMENTO DE VAGAS"
echo "====================================="

echo ""
echo "1️⃣ VERIFICANDO CONFIGURAÇÕES ATUAIS"
echo "==================================="

# Verificar arquivo .env
if [ -f ".env" ]; then
    echo "✅ Arquivo .env encontrado"
    echo ""
    echo "📋 Configurações relevantes:"
    echo "CSRF_TRUSTED_ORIGINS:"
    grep "CSRF_TRUSTED_ORIGINS" .env
    echo ""
    echo "CSRF_COOKIE_SECURE:"
    grep "CSRF_COOKIE_SECURE" .env
    echo ""
    echo "DEBUG:"
    grep "DEBUG" .env
else
    echo "❌ Arquivo .env não encontrado!"
fi

echo ""
echo "2️⃣ TESTANDO CONECTIVIDADE DO SITE"
echo "================================="

echo "🌐 Testando acesso ao site..."
response=$(curl -s -o /dev/null -w "%{http_code}" https://rh.institutoacqua.org.br/)
echo "Status HTTP: $response"

if [ "$response" = "200" ] || [ "$response" = "302" ]; then
    echo "✅ Site está acessível"
else
    echo "❌ Problema de conectividade"
fi

echo ""
echo "3️⃣ VERIFICANDO CONTAINERS DOCKER"
echo "================================"

if command -v docker &> /dev/null; then
    echo "📋 Containers relacionados ao projeto:"
    sudo docker ps --filter "name=rh-acqua" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "❌ Erro ao listar containers"
    
    echo ""
    echo "📋 Logs recentes do container web (últimas 30 linhas):"
    web_container=$(sudo docker ps --filter "name=rh-acqua" --format "{{.Names}}" | grep web | head -1)
    if [ ! -z "$web_container" ]; then
        echo "Container encontrado: $web_container"
        sudo docker logs --tail 30 $web_container 2>/dev/null || echo "❌ Erro ao obter logs"
    else
        echo "⚠️ Container web não encontrado"
    fi
else
    echo "❌ Docker não encontrado"
fi

echo ""
echo "4️⃣ TESTANDO FORMULÁRIO DE VAGA"
echo "=============================="

echo "🔍 Verificando se o formulário está acessível..."
form_response=$(curl -s -o /dev/null -w "%{http_code}" https://rh.institutoacqua.org.br/vacancies/create/)
echo "Status do formulário: $form_response"

if [ "$form_response" = "200" ] || [ "$form_response" = "302" ]; then
    echo "✅ Formulário de criação de vaga está acessível"
else
    echo "❌ Problema ao acessar formulário de criação de vaga"
fi

echo ""
echo "5️⃣ VERIFICANDO CSRF TOKEN"
echo "========================="

echo "🔍 Verificando se o CSRF token está sendo gerado..."
csrf_response=$(curl -s https://rh.institutoacqua.org.br/vacancies/create/ | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | head -1)
if [ ! -z "$csrf_response" ]; then
    echo "✅ CSRF token encontrado no formulário"
    echo "Token: $csrf_response"
else
    echo "❌ CSRF token não encontrado no formulário"
fi

echo ""
echo "6️⃣ TESTE DE POST SIMULADO"
echo "========================="

echo "🔍 Testando envio de dados para o formulário..."

# Obter CSRF token
csrf_token=$(curl -s https://rh.institutoacqua.org.br/vacancies/create/ | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | sed 's/name="csrfmiddlewaretoken" value="\([^"]*\)"/\1/')

if [ ! -z "$csrf_token" ]; then
    echo "CSRF Token obtido: $csrf_token"
    
    # Simular POST com dados mínimos
    post_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "Referer: https://rh.institutoacqua.org.br/vacancies/create/" \
        -d "csrfmiddlewaretoken=$csrf_token&title=Teste&description=Teste&requirements=Teste&hospital=1&department=1&location=Teste" \
        https://rh.institutoacqua.org.br/vacancies/create/)
    
    echo "Status do POST: $post_response"
    
    if [ "$post_response" = "200" ] || [ "$post_response" = "302" ]; then
        echo "✅ POST funcionou (pode ser redirecionamento de login)"
    elif [ "$post_response" = "403" ]; then
        echo "❌ Erro 403 - Problema de CSRF ou permissão"
    elif [ "$post_response" = "400" ]; then
        echo "⚠️ Erro 400 - Problema de validação de dados"
    else
        echo "❓ Status inesperado: $post_response"
    fi
else
    echo "❌ Não foi possível obter CSRF token"
fi

echo ""
echo "7️⃣ POSSÍVEIS CAUSAS DO PROBLEMA"
echo "==============================="

echo "🔍 Baseado no diagnóstico, as possíveis causas são:"
echo ""
echo "1. ❌ Problema de permissão do usuário"
echo "   - Usuário não tem role de recrutador"
echo "   - Usuário não está logado corretamente"
echo ""
echo "2. ❌ Problema de validação do formulário"
echo "   - Campos obrigatórios não preenchidos"
echo "   - Dados inválidos sendo enviados"
echo ""
echo "3. ❌ Problema de banco de dados"
echo "   - Conexão com banco não está funcionando"
echo "   - Tabelas não existem ou têm problemas"
echo ""
echo "4. ❌ Problema de configuração do Django"
echo "   - Configurações de produção incorretas"
echo "   - Middleware bloqueando requisições"
echo ""

echo "8️⃣ PRÓXIMOS PASSOS"
echo "=================="

echo "🎯 Para resolver o problema:"
echo ""
echo "1. Verifique se está logado como recrutador"
echo "2. Teste com dados válidos e completos"
echo "3. Verifique os logs do container Django"
echo "4. Teste em ambiente local para comparar"
echo ""

echo "📝 Para obter mais detalhes:"
echo "sudo docker logs <container_name> | tail -50"
echo ""

echo "✅ Diagnóstico concluído!"
