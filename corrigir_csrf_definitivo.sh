#!/bin/bash

echo "🔧 CORREÇÃO DEFINITIVA DO CSRF"
echo "=============================="

echo ""
echo "1️⃣ VERIFICANDO CONFIGURAÇÃO ATUAL"
echo "================================="

# Verificar se o arquivo .env existe
if [ -f ".env" ]; then
    echo "✅ Arquivo .env encontrado"
    echo ""
    echo "📋 Configuração atual do CSRF_TRUSTED_ORIGINS:"
    grep "CSRF_TRUSTED_ORIGINS" .env
else
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

echo ""
echo "2️⃣ CORRIGINDO CONFIGURAÇÃO DO CSRF"
echo "=================================="

# Remover todas as linhas de CSRF_TRUSTED_ORIGINS
echo "🗑️ Removendo configurações antigas..."
sed -i '/^CSRF_TRUSTED_ORIGINS=/d' .env

# Adicionar configuração correta
echo "➕ Adicionando configuração correta..."
echo "CSRF_TRUSTED_ORIGINS=https://rh.institutoacqua.org.br,http://rh.institutoacqua.org.br,https://158.220.108.114:8000,http://158.220.108.114:8000,http://localhost:8000,http://127.0.0.1:8000" >> .env

# Garantir que CSRF_COOKIE_SECURE está True
echo "🍪 Configurando CSRF_COOKIE_SECURE..."
sed -i 's/CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/' .env
sed -i 's/CSRF_COOKIE_SECURE=false/CSRF_COOKIE_SECURE=True/' .env

# Garantir que SESSION_COOKIE_SECURE está True
echo "🔒 Configurando SESSION_COOKIE_SECURE..."
sed -i 's/SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/' .env
sed -i 's/SESSION_COOKIE_SECURE=false/SESSION_COOKIE_SECURE=True/' .env

echo ""
echo "3️⃣ VERIFICANDO CONFIGURAÇÃO CORRIGIDA"
echo "====================================="

echo "📋 Nova configuração:"
grep -E "CSRF_TRUSTED_ORIGINS|CSRF_COOKIE_SECURE|SESSION_COOKIE_SECURE" .env

echo ""
echo "4️⃣ COMANDOS PARA EXECUTAR COM SUDO"
echo "=================================="

echo "Execute estes comandos para aplicar as correções:"
echo ""
echo "# 1. Parar todos os containers"
echo "sudo docker stop rh-acqua-web-1 rh-acqua-celery-1 rh-acqua-redis-1 rh-acqua-db-1 rh-acqua-celery-beat-1"
echo ""
echo "# 2. Remover containers (para forçar recriação)"
echo "sudo docker rm rh-acqua-web-1 rh-acqua-celery-1 rh-acqua-redis-1 rh-acqua-db-1 rh-acqua-celery-beat-1"
echo ""
echo "# 3. Recriar e iniciar containers"
echo "sudo docker compose up -d"
echo ""
echo "# 4. Verificar status"
echo "sudo docker ps"
echo ""
echo "# 5. Verificar logs do container web"
echo "sudo docker logs rh-acqua-web-1 --tail 20"
echo ""
echo "# 6. Testar URL"
echo "curl -I https://rh.institutoacqua.org.br/vacancies/vacancy/create/"

echo ""
echo "✅ Script de correção concluído!"
echo ""
echo "🎯 IMPORTANTE:"
echo "O problema pode ser que o container está usando uma versão em cache"
echo "das configurações. A remoção e recriação dos containers deve resolver."
