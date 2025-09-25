#!/bin/bash

# Correção final para erro 500 - problema específico de configuração
# Execute como root: sudo bash corrigir_500_final.sh

echo "=== Correção Final do Erro 500 ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_500_final.sh"
    exit 1
fi

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

echo "🔍 Problema identificado: conflito entre cache nginx e proxy"
echo "🎯 Solução: desabilitar cache especificamente para o subdomínio rh"

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.500fix.$(date +%Y%m%d_%H%M%S)"

echo "📝 Fazendo correção específica para o erro 500..."

# Localizar o bloco do servidor rh e modificar as configurações de cache
# Primeiro, vamos comentar ou remover as linhas de cache problemáticas

# Encontrar o início do bloco do servidor rh
START_LINE=$(grep -n "server_name rh\.institutoacqua\.org\.br" "$CONF_FILE" | cut -d: -f1)
echo "Bloco rh inicia na linha: $START_LINE"

# Encontrar o fim do bloco (próxima chave de fechamento}
END_LINE=$(tail -n +$START_LINE "$CONF_FILE" | grep -n "^}" | head -1 | cut -d: -f1)
END_LINE=$((START_LINE + END_LINE - 1))
echo "Bloco rh termina na linha: $END_LINE"

# Criar um arquivo temporário com as modificações
echo "🔧 Aplicando correções no bloco rh..."

# Usar awk para modificar apenas o bloco específico
awk -v start=$START_LINE -v end=$END_LINE '
BEGIN { in_rh_block = 0 }

# Detectar início do bloco rh
NR == start { in_rh_block = 1 }

# Detectar fim do bloco rh  
NR == end { in_rh_block = 0 }

# Dentro do bloco rh, fazer modificações
{
    if (in_rh_block == 1) {
        # Desabilitar todas as configurações de cache
        if (/proxy_cache \$CPANEL_PROXY_CACHE/) {
            print "        proxy_cache off;"
        } else if (/proxy_no_cache \$CPANEL_SKIP_PROXY_CACHING/) {
            print "        proxy_no_cache 1;"
        } else if (/proxy_cache_bypass \$CPANEL_SKIP_PROXY_CACHING/) {
            print "        proxy_cache_bypass 1;"
        } else if (/proxy_cache_valid/) {
            print "        # " $0 " # Desabilitado para evitar erro 500"
        } else if (/proxy_cache_/) {
            print "        # " $0 " # Desabilitado para evitar erro 500"
        } else {
            print $0
        }
    } else {
        print $0
    }
}
' "$CONF_FILE" > /tmp/nginx_fixed_500.conf

# Verificar se arquivo foi gerado corretamente
if [ -s /tmp/nginx_fixed_500.conf ]; then
    echo "✅ Arquivo corrigido gerado"
    
    # Substituir o arquivo original
    cp /tmp/nginx_fixed_500.conf "$CONF_FILE"
    
    # Testar configuração
    echo "🔍 Testando configuração corrigida..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração nginx válida!"
        
        # Limpar cache nginx problemático
        echo "🧹 Limpando cache nginx..."
        rm -rf /var/cache/ea-nginx/proxy/institutoacquaor/* 2>/dev/null
        
        # Recarregar nginx
        echo "🔄 Recarregando nginx..."
        systemctl reload nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx recarregado com sucesso!"
            
            # Aguardar para limpeza de cache
            echo "⏳ Aguardando 10 segundos para limpeza de cache..."
            sleep 10
            
            # Testes progressivos
            echo "🧪 Testes progressivos..."
            
            for i in {1..5}; do
                echo "--- Teste $i/5 ---"
                
                # Fazer requisição com headers específicos
                RESPONSE=$(curl -s -I -H "Host: rh.institutoacqua.org.br" -H "Cache-Control: no-cache" http://rh.institutoacqua.org.br/ 2>/dev/null)
                
                if [ -n "$RESPONSE" ]; then
                    STATUS=$(echo "$RESPONSE" | head -1 | tr -d '\r')
                    SERVER=$(echo "$RESPONSE" | grep -i "server:" | tr -d '\r')
                    
                    echo "Status: $STATUS"
                    echo "$SERVER"
                    
                    if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                        echo ""
                        echo "🎉🎉🎉 SUCESSO TOTAL! 🎉🎉🎉"
                        echo "✅ Django funcionando via rh.institutoacqua.org.br"
                        echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
                        
                        # Teste adicional
                        FINAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)
                        echo "📊 Status code final: $FINAL_STATUS"
                        break
                        
                    elif echo "$RESPONSE" | grep -q "302\|301"; then
                        echo "🎉 SUCESSO! Redirecionamento funcionando"
                        echo "✅ Django ativo via domínio"
                        break
                        
                    elif echo "$RESPONSE" | grep -q "200"; then
                        echo "✅ Resposta 200 - verificando conteúdo..."
                        
                        CONTENT_TEST=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 500)
                        if echo "$CONTENT_TEST" | grep -qi "RH\|Django\|login\|form\|html\|doctype"; then
                            echo "🎉 SUCESSO! Conteúdo Django detectado"
                            break
                        else
                            echo "⚠️ Conteúdo ainda pode ser listagem"
                        fi
                        
                    elif echo "$RESPONSE" | grep -q "500"; then
                        echo "❌ Ainda erro 500"
                        
                    elif echo "$RESPONSE" | grep -q "502\|503\|504"; then
                        echo "⚠️ Erro de conexão com Django"
                        
                    else
                        echo "❓ Resposta inesperada"
                    fi
                else
                    echo "❌ Sem resposta do servidor"
                fi
                
                if [ $i -lt 5 ]; then
                    echo "Aguardando 5s..."
                    sleep 5
                fi
            done
            
            echo ""
            echo "📊 Comparação final:"
            echo "Django local:  $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
            echo "Via domínio:   $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"
            
        else
            echo "❌ Erro ao recarregar nginx"
            echo "Restaurando backup..."
            cp "${CONF_FILE}.backup.500fix"* "$CONF_FILE" 2>/dev/null
            systemctl reload nginx
        fi
    else
        echo "❌ Erro na configuração nginx"
        echo "Restaurando backup..."
        cp "${CONF_FILE}.backup.500fix"* "$CONF_FILE" 2>/dev/null
        echo "Detalhes do erro:"
        nginx -t
    fi
else
    echo "❌ Erro ao gerar arquivo corrigido"
fi

# Limpeza
rm -f /tmp/nginx_fixed_500.conf

echo ""
echo "=== Correção 500 Finalizada ==="
echo "📁 Backup: ${CONF_FILE}.backup.500fix.*"
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
