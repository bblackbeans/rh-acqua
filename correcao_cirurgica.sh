#!/bin/bash

# Correção cirúrgica - substituir apenas no bloco correto
# Execute como root: sudo bash correcao_cirurgica.sh

echo "=== Correção Cirúrgica do Nginx ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash correcao_cirurgica.sh"
    exit 1
fi

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

echo "📝 Fazendo backup da configuração atual..."
cp "$CONF_FILE" "${CONF_FILE}.backup.cirurgica.$(date +%Y%m%d_%H%M%S)"

echo "🔍 Identificando linha exata para modificar..."

# Encontrar número da linha do proxy_pass dentro do bloco rh.institutoacqua.org.br
START_LINE=$(grep -n "server_name rh\.institutoacqua\.org\.br" "$CONF_FILE" | cut -d: -f1)
echo "Servidor rh inicia na linha: $START_LINE"

if [ -z "$START_LINE" ]; then
    echo "❌ Bloco do servidor rh não encontrado"
    exit 1
fi

# Encontrar a linha do proxy_pass depois do START_LINE
PROXY_LINE=$(tail -n +$START_LINE "$CONF_FILE" | grep -n "proxy_pass.*CPANEL_APACHE_PROXY_PASS" | head -1 | cut -d: -f1)

if [ -z "$PROXY_LINE" ]; then
    echo "❌ Linha proxy_pass não encontrada no bloco rh"
    exit 1
fi

# Calcular linha absoluta
ABSOLUTE_LINE=$((START_LINE + PROXY_LINE - 1))
echo "Proxy_pass encontrado na linha absoluta: $ABSOLUTE_LINE"

# Mostrar contexto da linha
echo "Contexto atual:"
sed -n "$((ABSOLUTE_LINE-2)),$((ABSOLUTE_LINE+2))p" "$CONF_FILE"

echo ""
echo "🎯 Aplicando correção cirúrgica na linha $ABSOLUTE_LINE..."

# Substituir apenas essa linha específica
sed -i "${ABSOLUTE_LINE}s/proxy_pass \$CPANEL_APACHE_PROXY_PASS;/proxy_pass http:\/\/127.0.0.1:8000;/" "$CONF_FILE"

echo "✅ Linha modificada"

# Mostrar resultado
echo "Resultado da modificação:"
sed -n "$((ABSOLUTE_LINE-2)),$((ABSOLUTE_LINE+2))p" "$CONF_FILE"

echo ""
echo "🔍 Testando configuração nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx válida!"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso!"
        
        # Aguardar propagação
        echo "⏳ Aguardando 8 segundos para propagação..."
        sleep 8
        
        # Teste final
        echo "🔍 Teste final do domínio..."
        
        echo "--- Headers de resposta ---"
        RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
        echo "$RESPONSE" | head -5
        
        echo ""
        if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
            echo "🎉🎉🎉 PERFEITO! DJANGO FUNCIONANDO! 🎉🎉🎉"
            echo "✅ rh.institutoacqua.org.br → Django ativo"
            echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
        elif echo "$RESPONSE" | grep -q "302"; then
            echo "🎉 SUCESSO! Redirecionamento Django detectado"
            echo "✅ rh.institutoacqua.org.br → Django funcionando"
            echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
        elif echo "$RESPONSE" | grep -q "200"; then
            echo "✅ Resposta 200 - verificar no navegador"
            echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
            
            # Teste de conteúdo
            CONTENT_CHECK=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 300)
            if echo "$CONTENT_CHECK" | grep -qi "RH\|Django\|login\|form\|<!DOCTYPE"; then
                echo "✅ Conteúdo confirma: É Django!"
            fi
        else
            echo "⚠️ Resposta diferente - verificar manualmente"
        fi
        
        echo ""
        echo "📊 Comparação final:"
        echo "Django direto: $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
        echo "Via domínio:   $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"
        
    else
        echo "❌ Erro ao recarregar nginx"
        echo "Restaurando backup..."
        cp "${CONF_FILE}.backup.cirurgica"* "$CONF_FILE" 2>/dev/null
        systemctl reload nginx
    fi
else
    echo "❌ Erro na configuração nginx"
    echo "Restaurando backup..."
    cp "${CONF_FILE}.backup.cirurgica"* "$CONF_FILE" 2>/dev/null
    echo "Detalhes do erro:"
    nginx -t
fi

echo ""
echo "=== Correção Cirúrgica Finalizada ==="
echo "📁 Backup: ${CONF_FILE}.backup.cirurgica.*"
echo "🌐 Resultado: http://rh.institutoacqua.org.br/"
