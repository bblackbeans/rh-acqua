#!/bin/bash

echo "🔧 CORRIGINDO CONFIGURAÇÕES DE CSRF PARA HTTPS"
echo "=============================================="

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado. Criando a partir do env_config.txt..."
    cp env_config.txt .env
fi

echo "📋 Configurações atuais:"
echo "CSRF_TRUSTED_ORIGINS:"
grep "CSRF_TRUSTED_ORIGINS" .env || echo "Não encontrado"
echo ""
echo "CSRF_COOKIE_SECURE:"
grep "CSRF_COOKIE_SECURE" .env || echo "Não encontrado"
echo ""

# Atualizar CSRF_TRUSTED_ORIGINS para incluir HTTPS
echo "🔐 Atualizando CSRF_TRUSTED_ORIGINS para HTTPS..."

# Remover configuração antiga se existir
sed -i '/^CSRF_TRUSTED_ORIGINS=/d' .env

# Adicionar nova configuração com HTTPS
echo "CSRF_TRUSTED_ORIGINS=https://rh.institutoacqua.org.br,http://rh.institutoacqua.org.br,https://158.220.108.114:8000,http://158.220.108.114:8000,http://localhost:8000,http://127.0.0.1:8000" >> .env

# Atualizar CSRF_COOKIE_SECURE para True (necessário para HTTPS)
echo "🍪 Atualizando CSRF_COOKIE_SECURE para True..."
sed -i 's/CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/' .env
sed -i 's/CSRF_COOKIE_SECURE=false/CSRF_COOKIE_SECURE=True/' .env

# Atualizar SESSION_COOKIE_SECURE para True (necessário para HTTPS)
echo "🔒 Atualizando SESSION_COOKIE_SECURE para True..."
sed -i 's/SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/' .env
sed -i 's/SESSION_COOKIE_SECURE=false/SESSION_COOKIE_SECURE=True/' .env

# Adicionar configurações adicionais de segurança para HTTPS
echo "🛡️ Adicionando configurações de segurança para HTTPS..."

# Verificar se as configurações já existem
if ! grep -q "SECURE_SSL_REDIRECT" .env; then
    echo "SECURE_SSL_REDIRECT=True" >> .env
fi

if ! grep -q "SECURE_BROWSER_XSS_FILTER" .env; then
    echo "SECURE_BROWSER_XSS_FILTER=True" >> .env
fi

if ! grep -q "SECURE_CONTENT_TYPE_NOSNIFF" .env; then
    echo "SECURE_CONTENT_TYPE_NOSNIFF=True" >> .env
fi

if ! grep -q "X_FRAME_OPTIONS" .env; then
    echo "X_FRAME_OPTIONS=DENY" >> .env
fi

echo ""
echo "✅ Configurações atualizadas:"
echo "=============================="
echo "CSRF_TRUSTED_ORIGINS:"
grep "CSRF_TRUSTED_ORIGINS" .env
echo ""
echo "CSRF_COOKIE_SECURE:"
grep "CSRF_COOKIE_SECURE" .env
echo ""
echo "SESSION_COOKIE_SECURE:"
grep "SESSION_COOKIE_SECURE" .env
echo ""
echo "Configurações de segurança adicionadas:"
grep -E "SECURE_|X_FRAME" .env

echo ""
echo "🔄 Reiniciando containers para aplicar as mudanças..."
echo "====================================================="

# Tentar reiniciar os containers
if command -v docker-compose &> /dev/null; then
    echo "Usando docker-compose..."
    docker-compose restart web
elif command -v docker &> /dev/null; then
    echo "Usando docker..."
    docker restart $(docker ps -q --filter "name=rh-acqua")
else
    echo "⚠️ Docker não encontrado. Reinicie manualmente os containers."
fi

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "==================="
echo "1. Verifique se os containers reiniciaram corretamente"
echo "2. Teste o salvamento de vagas no ambiente online"
echo "3. Se ainda houver problemas, verifique os logs do nginx"
echo ""
echo "📝 Para verificar os logs:"
echo "   docker logs <container_name>"
echo ""
echo "✅ Correção concluída!"
