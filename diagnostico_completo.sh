#!/bin/bash

echo "🔍 DIAGNÓSTICO COMPLETO DO PROBLEMA DE CSRF"
echo "==========================================="

echo ""
echo "1️⃣ VERIFICANDO CONFIGURAÇÕES DO DJANGO"
echo "======================================"

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
    echo "SESSION_COOKIE_SECURE:"
    grep "SESSION_COOKIE_SECURE" .env
    echo ""
    echo "ALLOWED_HOSTS:"
    grep "ALLOWED_HOSTS" .env
else
    echo "❌ Arquivo .env não encontrado!"
fi

echo ""
echo "2️⃣ TESTANDO CONECTIVIDADE HTTPS"
echo "==============================="

echo "🌐 Testando acesso HTTPS ao site..."
response=$(curl -s -o /dev/null -w "%{http_code}" https://rh.institutoacqua.org.br/)
echo "Status HTTP: $response"

if [ "$response" = "200" ] || [ "$response" = "302" ]; then
    echo "✅ Site está acessível via HTTPS"
else
    echo "❌ Problema de conectividade HTTPS"
fi

echo ""
echo "3️⃣ VERIFICANDO HEADERS DE SEGURANÇA"
echo "==================================="

echo "🔍 Analisando headers de resposta..."
curl -I https://rh.institutoacqua.org.br/ 2>/dev/null | grep -E "(Set-Cookie|X-|Strict-Transport-Security)" || echo "Nenhum header de segurança encontrado"

echo ""
echo "4️⃣ VERIFICANDO CONFIGURAÇÃO DO NGINX"
echo "===================================="

# Verificar se há configuração específica do nginx
if [ -f "nginx.conf" ]; then
    echo "✅ Arquivo nginx.conf encontrado"
    echo "📋 Configuração de proxy:"
    grep -A 10 -B 2 "proxy_pass" nginx.conf
else
    echo "⚠️ Arquivo nginx.conf não encontrado"
fi

if [ -f ".nginx/rh_proxy.conf" ]; then
    echo "✅ Arquivo .nginx/rh_proxy.conf encontrado"
    echo "📋 Configuração de proxy:"
    grep -A 10 -B 2 "proxy_pass" .nginx/rh_proxy.conf
else
    echo "⚠️ Arquivo .nginx/rh_proxy.conf não encontrado"
fi

echo ""
echo "5️⃣ VERIFICANDO CONTAINERS DOCKER"
echo "================================"

if command -v docker &> /dev/null; then
    echo "📋 Containers relacionados ao projeto:"
    docker ps --filter "name=rh-acqua" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "❌ Erro ao listar containers"
    
    echo ""
    echo "📋 Logs recentes do container web (últimas 20 linhas):"
    web_container=$(docker ps --filter "name=rh-acqua" --format "{{.Names}}" | grep web | head -1)
    if [ ! -z "$web_container" ]; then
        docker logs --tail 20 $web_container 2>/dev/null || echo "❌ Erro ao obter logs"
    else
        echo "⚠️ Container web não encontrado"
    fi
else
    echo "❌ Docker não encontrado"
fi

echo ""
echo "6️⃣ TESTE DE CSRF TOKEN"
echo "======================"

echo "🔍 Verificando se o CSRF token está sendo gerado..."
csrf_response=$(curl -s https://rh.institutoacqua.org.br/users/login/ | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | head -1)
if [ ! -z "$csrf_response" ]; then
    echo "✅ CSRF token encontrado na página de login"
    echo "Token: $csrf_response"
else
    echo "❌ CSRF token não encontrado na página de login"
fi

echo ""
echo "7️⃣ RESUMO E RECOMENDAÇÕES"
echo "========================="

echo "🎯 PROBLEMA IDENTIFICADO:"
echo "O site está rodando em HTTPS mas as configurações de CSRF estavam configuradas para HTTP."
echo "Isso causa erro 403 Forbidden ao tentar salvar formulários."

echo ""
echo "✅ CORREÇÕES APLICADAS:"
echo "1. CSRF_COOKIE_SECURE=True"
echo "2. SESSION_COOKIE_SECURE=True"
echo "3. CSRF_TRUSTED_ORIGINS inclui HTTPS"
echo "4. Configurações de segurança adicionais"

echo ""
echo "🔄 PRÓXIMOS PASSOS:"
echo "1. Execute: sudo ./reiniciar_containers.sh"
echo "2. Teste o salvamento de vagas"
echo "3. Se ainda houver problemas, verifique os logs"

echo ""
echo "📞 SE O PROBLEMA PERSISTIR:"
echo "1. Verifique se o nginx está configurado corretamente"
echo "2. Confirme se o SSL está funcionando"
echo "3. Verifique se não há cache interferindo"
