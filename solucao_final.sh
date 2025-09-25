#!/bin/bash

# Solução final - substituição precisa sem duplicações
# Execute como root: sudo bash solucao_final.sh

echo "=== Solução Final - Substituição Precisa ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash solucao_final.sh"
    exit 1
fi

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

echo "📝 Fazendo backup..."
cp "$CONF_FILE" "${CONF_FILE}.backup.final.$(date +%Y%m%d_%H%M%S)"

echo "🔧 Aplicando solução precisa..."

# Solução: substituir APENAS a linha proxy_pass sem adicionar duplicados
# Usar uma abordagem mais precisa com awk

cat > /tmp/fix_nginx.awk << 'EOF'
BEGIN { 
    in_rh_server = 0
    in_location_root = 0
}

# Detectar início do servidor rh
/server_name rh\.institutoacqua\.org\.br/ {
    in_rh_server = 1
}

# Detectar fim do servidor (fechamento da chave)
/^}$/ {
    if (in_rh_server == 1) {
        in_rh_server = 0
    }
    if (in_location_root == 1) {
        in_location_root = 0
    }
}

# Detectar location / dentro do servidor rh
/location \/ {/ {
    if (in_rh_server == 1) {
        in_location_root = 1
    }
}

# Substituir proxy_pass apenas dentro do location / do servidor rh
{
    if (in_rh_server == 1 && in_location_root == 1 && /proxy_pass \$CPANEL_APACHE_PROXY_PASS/) {
        print "        proxy_pass http://127.0.0.1:8000;"
    } else {
        print $0
    }
}
EOF

# Aplicar correção
awk -f /tmp/fix_nginx.awk "$CONF_FILE" > /tmp/nginx_fixed.conf

# Verificar se arquivo foi gerado
if [ -s /tmp/nginx_fixed.conf ]; then
    echo "✅ Arquivo corrigido gerado"
    
    # Substituir arquivo original
    cp /tmp/nginx_fixed.conf "$CONF_FILE"
    
    echo "🔍 Testando configuração..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração nginx válida!"
        
        # Recarregar nginx
        echo "🔄 Recarregando nginx..."
        systemctl reload nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx recarregado com sucesso!"
            
            # Aguardar propagação
            sleep 5
            
            # Testar domínio múltiplas vezes
            echo "🔍 Testando domínio (múltiplos testes)..."
            
            for i in {1..5}; do
                echo "--- Teste $i ---"
                RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
                
                if [ -n "$RESPONSE" ]; then
                    STATUS=$(echo "$RESPONSE" | head -1 | tr -d '\r')
                    SERVER=$(echo "$RESPONSE" | grep -i "server:" | tr -d '\r' || echo "Server: não encontrado")
                    
                    echo "Status: $STATUS"
                    echo "$SERVER"
                    
                    if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                        echo "🎉 SUCESSO TOTAL! Django funcionando via domínio!"
                        echo "✅ rh.institutoacqua.org.br → Django ativo"
                        break
                    elif echo "$RESPONSE" | grep -q "302"; then
                        echo "✅ Redirecionamento (provavelmente Django funcionando)"
                        break
                    elif echo "$RESPONSE" | grep -q "200"; then
                        echo "⚠️ Resposta 200 - verificar no navegador"
                    elif echo "$RESPONSE" | grep -q "500"; then
                        echo "❌ Ainda erro 500 - aguardando..."
                    else
                        echo "❓ Resposta diferente"
                    fi
                else
                    echo "❌ Sem resposta"
                fi
                
                if [ $i -lt 5 ]; then
                    echo "Aguardando 3s..."
                    sleep 3
                fi
            done
            
            echo ""
            echo "🧪 Teste final detalhado:"
            curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null | head -8
            
            echo ""
            echo "🌐 ACESSE NO NAVEGADOR: http://rh.institutoacqua.org.br/"
            
        else
            echo "❌ Erro ao recarregar nginx"
            echo "Restaurando backup..."
            cp "${CONF_FILE}.backup.final"* "$CONF_FILE" 2>/dev/null
            systemctl reload nginx
        fi
    else
        echo "❌ Erro na configuração"
        echo "Restaurando backup..."
        cp "${CONF_FILE}.backup.final"* "$CONF_FILE" 2>/dev/null
        echo "Detalhes do erro:"
        nginx -t
    fi
else
    echo "❌ Erro ao gerar arquivo corrigido"
fi

# Limpeza
rm -f /tmp/fix_nginx.awk /tmp/nginx_fixed.conf

echo ""
echo "=== Solução Final Concluída ==="
echo "📁 Backups disponíveis: ${CONF_FILE}.backup.final.*"
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
