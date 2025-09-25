#!/bin/bash

# Script para corrigir erro 500 - método diferente
# Execute como root: sudo bash corrigir_500.sh

echo "=== Corrigindo Erro 500 (Duplicate Location) ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_500.sh"
    exit 1
fi

# Remover arquivo problemático
echo "🗑️ Removendo arquivo com duplicate location..."
rm -f /etc/nginx/conf.d/users/institutoacquaor/rh.institutoacqua.org.br/django_proxy.conf

# Abordagem diferente: modificar o arquivo principal diretamente
CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

echo "📝 Fazendo backup do arquivo principal..."
cp "$CONF_FILE" "${CONF_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

echo "🔧 Modificando configuração principal diretamente..."

# Usar sed para substituir apenas o proxy_pass na seção do rh
sed -i '/server_name rh\.institutoacqua\.org\.br/,/^}$/{
    s/proxy_pass \$CPANEL_APACHE_PROXY_PASS/proxy_pass http:\/\/127.0.0.1:8000/g
}' "$CONF_FILE"

# Adicionar headers necessários após o proxy_pass
sed -i '/server_name rh\.institutoacqua\.org\.br/,/^}$/{
    /proxy_pass http:\/\/127\.0\.0\.1:8000/a\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
        proxy_cache off;\
        proxy_no_cache 1;\
        proxy_cache_bypass 1;
}' "$CONF_FILE"

echo "✅ Configuração modificada no arquivo principal"

# Testar configuração
echo "🔍 Testando configuração nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx válida"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso"
        
        # Aguardar um pouco
        sleep 3
        
        # Testar domínio
        echo "🔍 Testando domínio..."
        
        for i in {1..3}; do
            echo "Teste $i:"
            RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
            STATUS=$(echo "$RESPONSE" | head -1)
            SERVER=$(echo "$RESPONSE" | grep -i "server:" || echo "Server: não encontrado")
            
            echo "  Status: $(echo $STATUS | tr -d '\r')"
            echo "  $SERVER"
            
            if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                echo "🎉 SUCESSO! Django funcionando"
                break
            fi
            
            if [ $i -lt 3 ]; then
                echo "  Aguardando 2s..."
                sleep 2
            fi
        done
        
        # Teste final
        echo ""
        echo "🧪 Teste final completo:"
        curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null | head -5
        
    else
        echo "❌ Erro ao recarregar nginx"
        echo "Restaurando backup..."
        cp "${CONF_FILE}.backup"* "$CONF_FILE" 2>/dev/null
        systemctl reload nginx
    fi
else
    echo "❌ Erro na configuração"
    echo "Restaurando backup..."
    cp "${CONF_FILE}.backup"* "$CONF_FILE" 2>/dev/null
    nginx -t
fi

echo ""
echo "=== Correção 500 Finalizada ==="
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
