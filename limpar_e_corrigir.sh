#!/bin/bash

# Script para limpar configurações antigas e aplicar as novas
# Execute como root: sudo bash limpar_e_corrigir.sh

echo "=== Limpando e Corrigindo Configuração Nginx ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash limpar_e_corrigir.sh"
    exit 1
fi

# 1. Remover arquivos problemáticos antigos
echo "🗑️ Removendo configurações antigas problemáticas..."
rm -f /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf
rm -rf /etc/nginx/conf.d/users/institutoacquaor/rh.institutoacqua.org.br/

echo "✅ Arquivos antigos removidos"

# 2. Verificar se as configurações WHM foram criadas corretamente
USERDATA_HTTP="/etc/nginx/conf.d/userdata/std/2_4/institutoacquaor/rh.institutoacqua.org.br/rh_django_proxy.conf"
USERDATA_SSL="/etc/nginx/conf.d/userdata/ssl/2_4/institutoacquaor/rh.institutoacqua.org.br/rh_django_proxy.conf"

echo "🔍 Verificando configurações WHM..."

if [ -f "$USERDATA_HTTP" ]; then
    echo "✅ Configuração HTTP encontrada: $USERDATA_HTTP"
else
    echo "❌ Configuração HTTP não encontrada, criando..."
    mkdir -p "$(dirname "$USERDATA_HTTP")"
    cat > "$USERDATA_HTTP" << 'EOF'
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    proxy_buffering off;
    proxy_cache off;
    proxy_no_cache 1;
    proxy_cache_bypass 1;
    proxy_redirect off;
}

location /static/ {
    alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    access_log off;
}

location /media/ {
    alias /home/institutoacquaor/public_html/rh-acqua/media/;
    expires 7d; 
    add_header Cache-Control "public";
    access_log off;
}
EOF
    echo "✅ Configuração HTTP criada"
fi

if [ -f "$USERDATA_SSL" ]; then
    echo "✅ Configuração SSL encontrada: $USERDATA_SSL"
else
    echo "❌ Configuração SSL não encontrada, criando..."
    mkdir -p "$(dirname "$USERDATA_SSL")"
    cp "$USERDATA_HTTP" "$USERDATA_SSL"
    echo "✅ Configuração SSL criada"
fi

# 3. Reconstruir configuração nginx
echo "🔨 Reconstruindo configuração nginx..."
/usr/local/cpanel/scripts/rebuildhttpdconf

# 4. Testar configuração
echo "🔍 Testando configuração nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx válida"
    
    # 5. Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso"
        
        # 6. Aguardar um pouco
        sleep 5
        
        # 7. Testar Django local
        echo "🔍 Testando Django local..."
        DJANGO_LOCAL=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
        echo "Django local status: $DJANGO_LOCAL"
        
        # 8. Testar domínio
        echo "🔍 Testando domínio rh.institutoacqua.org.br..."
        
        # Teste HTTP
        echo "--- Teste HTTP ---"
        curl -I http://rh.institutoacqua.org.br/ 2>/dev/null | head -3
        
        # Verificar se está funcionando
        DOMAIN_RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
        
        if echo "$DOMAIN_RESPONSE" | grep -q "Server: gunicorn"; then
            echo "🎉 SUCESSO! Django funcionando através do domínio"
            echo "✅ rh.institutoacqua.org.br → Django ativo"
        elif echo "$DOMAIN_RESPONSE" | grep -q "302\|200"; then
            echo "⚠️ Domínio responde mas pode precisar de mais tempo"
            echo "Aguarde 2-3 minutos e teste novamente"
        else
            echo "❌ Domínio ainda não redirecionando"
        fi
        
        # 9. Mostrar status final
        echo ""
        echo "=== STATUS FINAL ==="
        echo "Django (127.0.0.1:8000): $DJANGO_LOCAL"
        echo "Domínio: $(echo "$DOMAIN_RESPONSE" | head -1 | tr -d '\r')"
        echo ""
        echo "🌐 Teste manual: http://rh.institutoacqua.org.br/"
        
    else
        echo "❌ Erro ao recarregar nginx"
        journalctl -u nginx --no-pager -n 10
    fi
else
    echo "❌ Configuração nginx ainda com erro"
    echo "Detalhes do erro:"
    nginx -t
fi

echo ""
echo "=== Limpeza e Correção Finalizada ==="
