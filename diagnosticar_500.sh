#!/bin/bash

# Script para diagnosticar e corrigir erro 500
# Execute como root: sudo bash diagnosticar_500.sh

echo "=== Diagnóstico e Correção do Erro 500 ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash diagnosticar_500.sh"
    exit 1
fi

echo "🔍 Verificando logs de erro do nginx..."
echo "--- Últimas 15 linhas do log de erro ---"
tail -15 /var/log/nginx/error.log 2>/dev/null | grep -v "access forbidden" | tail -10

echo ""
echo "🔍 Verificando se Django está realmente rodando..."
DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
echo "Django local status: $DJANGO_STATUS"

if [ "$DJANGO_STATUS" != "302" ] && [ "$DJANGO_STATUS" != "200" ]; then
    echo "❌ Django não está respondendo corretamente"
    echo "Verificando containers Docker..."
    
    # Verificar se Docker está rodando
    if command -v docker &> /dev/null; then
        echo "--- Status dos containers ---"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Sem containers rodando ou sem permissão"
    fi
    
    echo ""
    echo "Verificando processo na porta 8000..."
    netstat -tlnp | grep :8000 || echo "Nada rodando na porta 8000"
    
    exit 1
fi

echo "✅ Django respondendo corretamente"

# O problema pode ser nos headers ou configuração de proxy
echo ""
echo "🔧 Tentando correção adicional - melhorando configuração de proxy..."

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.antes_headers.$(date +%Y%m%d_%H%M%S)"

# Encontrar a linha onde fizemos a modificação e adicionar headers
LINE_NUM=$(grep -n "proxy_pass http://127.0.0.1:8000" "$CONF_FILE" | cut -d: -f1)

if [ -n "$LINE_NUM" ]; then
    echo "📍 Linha do proxy_pass encontrada: $LINE_NUM"
    
    # Adicionar headers essenciais após a linha do proxy_pass
    sed -i "${LINE_NUM}a\\
        proxy_set_header Host \$host;\\
        proxy_set_header X-Real-IP \$remote_addr;\\
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
        proxy_set_header X-Forwarded-Proto \$scheme;" "$CONF_FILE"
    
    echo "✅ Headers de proxy adicionados"
    
    # Testar configuração
    echo "🔍 Testando nova configuração..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração válida"
        
        # Recarregar nginx
        echo "🔄 Recarregando nginx..."
        systemctl reload nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx recarregado"
            
            # Aguardar um pouco
            sleep 5
            
            # Testar novamente
            echo "🔍 Testando após correção..."
            
            for i in {1..3}; do
                echo "--- Teste $i ---"
                RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
                STATUS=$(echo "$RESPONSE" | head -1 | tr -d '\r')
                
                echo "Status: $STATUS"
                
                if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                    echo "🎉 SUCESSO! Django funcionando via domínio!"
                    echo "✅ Headers: Django/gunicorn detectado"
                    break
                elif echo "$RESPONSE" | grep -q "302\|301"; then
                    echo "🎉 SUCESSO! Redirecionamento Django detectado!"
                    break
                elif echo "$RESPONSE" | grep -q "200"; then
                    echo "✅ Resposta 200 - provavelmente funcionando"
                    
                    # Teste de conteúdo
                    CONTENT=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 200)
                    if echo "$CONTENT" | grep -qi "django\|rh\|login\|html\|doctype"; then
                        echo "✅ Conteúdo confirma Django funcionando!"
                        break
                    fi
                elif echo "$RESPONSE" | grep -q "500"; then
                    echo "❌ Ainda erro 500"
                    if [ $i -eq 3 ]; then
                        echo "🔍 Verificando logs específicos..."
                        journalctl -u nginx --no-pager -n 5 | grep -i error || echo "Sem erros recentes no journal"
                    fi
                fi
                
                if [ $i -lt 3 ]; then
                    echo "Aguardando 3s..."
                    sleep 3
                fi
            done
            
        else
            echo "❌ Erro ao recarregar nginx"
            cp "${CONF_FILE}.backup.antes_headers"* "$CONF_FILE" 2>/dev/null
            systemctl reload nginx
        fi
    else
        echo "❌ Erro na configuração"
        cp "${CONF_FILE}.backup.antes_headers"* "$CONF_FILE" 2>/dev/null
        nginx -t
    fi
else
    echo "❌ Linha proxy_pass não encontrada"
fi

echo ""
echo "🧪 Status final:"
echo "Django direto: $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
echo "Via domínio:   $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"

echo ""
echo "🌐 TESTE NO NAVEGADOR: http://rh.institutoacqua.org.br/"
echo ""
echo "=== Diagnóstico Finalizado ==="
