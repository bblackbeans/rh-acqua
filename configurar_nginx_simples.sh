#!/bin/bash

# Script simples para configurar nginx - Execute como root
# sudo bash configurar_nginx_simples.sh

echo "=== Configuração Simples do Nginx ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash configurar_nginx_simples.sh"
    exit 1
fi

# Localizar arquivo de configuração
CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

if [ ! -f "$CONF_FILE" ]; then
    echo "❌ Arquivo $CONF_FILE não encontrado"
    echo "Localizando configurações nginx..."
    find /etc/nginx -name "*institutoacquaor*" -type f
    exit 1
fi

echo "✅ Encontrado: $CONF_FILE"

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup criado"

# Criar configuração temporária
cat > /tmp/rh_nginx_config << 'EOF'
# Configuração para rh.institutoacqua.org.br - PROXY PARA DJANGO
server {
    server_name rh.institutoacqua.org.br www.rh.institutoacqua.org.br;
    listen 80;
    listen [::]:80;
    listen 443 ssl;
    listen [::]:443 ssl;

    ssl_certificate /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;
    ssl_certificate_key /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;
    }

    location /media/ {
        alias /home/institutoacquaor/public_html/rh-acqua/media/;
    }
}
EOF

echo "📝 Adicionando configuração de proxy..."

# Adicionar configuração ao final do arquivo
cat /tmp/rh_nginx_config >> "$CONF_FILE"

echo "✅ Configuração adicionada"

# Testar e recarregar
nginx -t && systemctl reload nginx

echo "🎉 Configuração concluída!"
echo "Teste: http://rh.institutoacqua.org.br/"

rm /tmp/rh_nginx_config
