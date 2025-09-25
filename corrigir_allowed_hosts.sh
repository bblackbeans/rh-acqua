#!/bin/bash

# Script para corrigir ALLOWED_HOSTS e reiniciar Django
# Execute como root: sudo bash corrigir_allowed_hosts.sh

echo "=== Corrigindo ALLOWED_HOSTS do Django ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_allowed_hosts.sh"
    exit 1
fi

echo "🔍 Problema: Django não reconhece rh.institutoacqua.org.br"
echo "✅ Solução: Atualizar variáveis de ambiente e reiniciar containers"

# Verificar se .env existe, se não, criar
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp env_config.txt .env
fi

echo "🔧 Verificando configuração atual..."
echo "ALLOWED_HOSTS atual:"
grep "ALLOWED_HOSTS" .env

# Garantir que o domínio está nos ALLOWED_HOSTS
if ! grep -q "rh.institutoacqua.org.br" .env; then
    echo "➕ Adicionando domínio aos ALLOWED_HOSTS..."
    sed -i 's/ALLOWED_HOSTS=\(.*\)/ALLOWED_HOSTS=\1,rh.institutoacqua.org.br/' .env
fi

# Garantir que está nos CSRF_TRUSTED_ORIGINS
if ! grep -q "http://rh.institutoacqua.org.br" .env; then
    echo "➕ Adicionando domínio aos CSRF_TRUSTED_ORIGINS..."
    sed -i 's/CSRF_TRUSTED_ORIGINS=\(.*\)/CSRF_TRUSTED_ORIGINS=\1,http:\/\/rh.institutoacqua.org.br,https:\/\/rh.institutoacqua.org.br/' .env
fi

echo "✅ Configuração atualizada:"
grep "ALLOWED_HOSTS\|CSRF_TRUSTED" .env

echo ""
echo "🔄 Reiniciando containers Django..."

# Verificar se docker-compose está disponível
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose não encontrado"
    exit 1
fi

echo "Usando: $COMPOSE_CMD"

# Parar containers relacionados ao Django
echo "⏹️ Parando containers..."
$COMPOSE_CMD stop web celery celery-beat 2>/dev/null || echo "Alguns containers já estavam parados"

# Aguardar um pouco
sleep 3

# Reiniciar containers
echo "🚀 Iniciando containers com nova configuração..."
$COMPOSE_CMD up -d web celery celery-beat

if [ $? -eq 0 ]; then
    echo "✅ Containers reiniciados com sucesso!"
    
    # Aguardar Django inicializar
    echo "⏳ Aguardando Django inicializar (20 segundos)..."
    sleep 20
    
    # Testar Django local
    echo "🔍 Testando Django local..."
    for i in {1..5}; do
        DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)
        echo "Teste $i - Django local: $DJANGO_STATUS"
        
        if [ "$DJANGO_STATUS" = "302" ] || [ "$DJANGO_STATUS" = "200" ]; then
            echo "✅ Django funcionando localmente"
            break
        fi
        
        if [ $i -lt 5 ]; then
            echo "Aguardando 5s..."
            sleep 5
        fi
    done
    
    echo ""
    echo "🌐 Testando domínio rh.institutoacqua.org.br..."
    
    for i in {1..6}; do
        echo "--- Teste domínio $i/6 ---"
        
        RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
        
        if [ -n "$RESPONSE" ]; then
            STATUS=$(echo "$RESPONSE" | head -1 | tr -d '\r')
            SERVER=$(echo "$RESPONSE" | grep -i "server:" | tr -d '\r')
            
            echo "Status: $STATUS"
            echo "$SERVER"
            
            if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                echo ""
                echo "🎉🎉🎉 SUCESSO TOTAL! 🎉🎉🎉"
                echo "✅ Django funcionando via rh.institutoacqua.org.br"
                echo "🚀 ALLOWED_HOSTS corrigido!"
                echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
                break
                
            elif echo "$RESPONSE" | grep -q "302\|301"; then
                echo "🎉 SUCESSO! Redirecionamento Django funcionando"
                echo "✅ Sistema ativo via domínio"
                break
                
            elif echo "$RESPONSE" | grep -q "200"; then
                echo "✅ Resposta 200 - verificando se é Django..."
                
                # Testar conteúdo
                CONTENT=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 800)
                if echo "$CONTENT" | grep -qi "RH\|Django\|login\|form\|csrf\|html"; then
                    echo "🎉 SUCESSO! Django funcionando no domínio!"
                    break
                else
                    echo "⚠️ Resposta 200 mas conteúdo não parece Django"
                fi
                
            elif echo "$RESPONSE" | grep -q "400"; then
                echo "❌ Ainda erro 400 - ALLOWED_HOSTS pode precisar mais tempo"
                
            elif echo "$RESPONSE" | grep -q "500"; then
                echo "❌ Erro 500 retornou"
                
            else
                echo "❓ Resposta inesperada"
            fi
        else
            echo "❌ Sem resposta"
        fi
        
        if [ $i -lt 6 ]; then
            echo "Aguardando 10s para próximo teste..."
            sleep 10
        fi
    done
    
    echo ""
    echo "📊 Status final:"
    echo "Django local:  $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
    echo "Via domínio:   $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"
    
else
    echo "❌ Erro ao reiniciar containers"
    echo "Detalhes:"
    $COMPOSE_CMD logs web --tail=10 2>/dev/null || echo "Não foi possível obter logs"
fi

echo ""
echo "=== Correção ALLOWED_HOSTS Finalizada ==="
echo "📋 Configuração em: .env"
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
