#!/bin/bash

echo "🔍 VERIFICANDO CONFIGURAÇÕES DE CSRF"
echo "===================================="

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

echo "📋 Configurações atuais no .env:"
echo "================================"

echo ""
echo "🔐 CSRF_TRUSTED_ORIGINS:"
grep "CSRF_TRUSTED_ORIGINS" .env || echo "❌ Não encontrado"

echo ""
echo "🍪 CSRF_COOKIE_SECURE:"
grep "CSRF_COOKIE_SECURE" .env || echo "❌ Não encontrado"

echo ""
echo "🔒 SESSION_COOKIE_SECURE:"
grep "SESSION_COOKIE_SECURE" .env || echo "❌ Não encontrado"

echo ""
echo "🛡️ Configurações de segurança:"
grep -E "SECURE_|X_FRAME" .env || echo "❌ Nenhuma configuração de segurança encontrada"

echo ""
echo "🌐 ALLOWED_HOSTS:"
grep "ALLOWED_HOSTS" .env || echo "❌ Não encontrado"

echo ""
echo "🔧 DIAGNÓSTICO:"
echo "==============="

# Verificar se HTTPS está configurado corretamente
if grep -q "CSRF_COOKIE_SECURE=True" .env; then
    echo "✅ CSRF_COOKIE_SECURE está configurado para True (correto para HTTPS)"
else
    echo "❌ CSRF_COOKIE_SECURE não está configurado para True"
fi

if grep -q "SESSION_COOKIE_SECURE=True" .env; then
    echo "✅ SESSION_COOKIE_SECURE está configurado para True (correto para HTTPS)"
else
    echo "❌ SESSION_COOKIE_SECURE não está configurado para True"
fi

if grep -q "https://rh.institutoacqua.org.br" .env; then
    echo "✅ HTTPS está incluído nos CSRF_TRUSTED_ORIGINS"
else
    echo "❌ HTTPS não está incluído nos CSRF_TRUSTED_ORIGINS"
fi

echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo "==================="
echo "1. Reinicie manualmente os containers Docker"
echo "2. Teste o salvamento de vagas"
echo "3. Se ainda houver problemas, verifique os logs"

echo ""
echo "🔄 Para reiniciar os containers manualmente:"
echo "   sudo docker-compose restart"
echo "   ou"
echo "   sudo docker restart <container_name>"
