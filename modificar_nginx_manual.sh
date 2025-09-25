#!/bin/bash

# Script para modificar manualmente a configuração nginx
# Execute como root: sudo bash modificar_nginx_manual.sh

echo "=== Modificação Manual do Nginx ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash modificar_nginx_manual.sh"
    exit 1
fi

# Arquivo de configuração
CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

# Remover arquivo problemático
rm -f /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf 2>/dev/null

echo "📋 Arquivo de configuração: $CONF_FILE"

# Verificar se arquivo existe
if [ ! -f "$CONF_FILE" ]; then
    echo "❌ Arquivo não encontrado: $CONF_FILE"
    exit 1
fi

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup criado"

# Encontrar linha específica e substituir
echo "🔍 Procurando configuração do subdomínio rh..."

# Usar sed para substituir a configuração do location / dentro do servidor rh
sed -i '/server_name rh\.institutoacqua\.org\.br/,/^}/{ 
    /location \/ {/,/^    }$/{
        s|proxy_pass.*|proxy_pass http://127.0.0.1:8000;|
        /proxy_pass http:\/\/127\.0\.0\.1:8000;/a\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
        proxy_cache off;\
        proxy_no_cache 1;\
        proxy_cache_bypass 1;
    }
}' "$CONF_FILE"

echo "✅ Configuração modificada"

# Testar configuração
echo "🔍 Testando configuração nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração válida"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso"
        
        # Aguardar propagação
        sleep 5
        
        # Testar resultado
        echo "🔍 Testando domínio..."
        curl -I http://rh.institutoacqua.org.br/ 2>/dev/null | head -5
        
        echo ""
        echo "🎉 Configuração aplicada!"
        echo "Teste o domínio: http://rh.institutoacqua.org.br/"
        
    else
        echo "❌ Erro ao recarregar nginx"
        echo "Restaurando backup..."
        cp "${CONF_FILE}.backup"* "$CONF_FILE"
        systemctl reload nginx
    fi
else
    echo "❌ Erro na configuração nginx"
    echo "Restaurando backup..."
    cp "${CONF_FILE}.backup"* "$CONF_FILE"
fi

echo "=== Finalizado ===" 
