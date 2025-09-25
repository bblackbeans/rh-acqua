#!/bin/bash

# Script para configurar nginx para proxy do Django
# Execute este script como root: sudo bash configurar_nginx_rh.sh

echo "=== Configurando nginx para rh.institutoacqua.org.br ==="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root"
    echo "Execute: sudo bash configurar_nginx_rh.sh"
    exit 1
fi

echo "✅ Executando como root"

# Criar backup da configuração atual
echo "📁 Criando backup da configuração atual..."
cp /etc/nginx/conf.d/users/institutoacquaor.conf /etc/nginx/conf.d/users/institutoacquaor.conf.backup.$(date +%Y%m%d_%H%M%S)

# Criar arquivo de configuração específico para o subdomínio rh
echo "📝 Criando configuração específica para rh.institutoacqua.org.br..."

# Verificar se diretório existe
mkdir -p /etc/nginx/conf.d/users/institutoacquaor/

cat > /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf << 'EOF'
# Configuração de proxy para rh.institutoacqua.org.br
# Sobrescreve a configuração padrão para fazer proxy para Django

server {
    server_name rh.institutoacqua.org.br www.rh.institutoacqua.org.br;
    listen 80;
    listen [::]:80;

    listen 443 ssl;
    listen [::]:443 ssl;

    # Configurações SSL (se existirem)
    ssl_certificate /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;
    ssl_certificate_key /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    # Configuração de proxy para Django
    location / {
        # Proxy para aplicação Django na porta 8000
        proxy_pass http://127.0.0.1:8000;
        
        # Headers necessários
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Configurações de timeout
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Desabilitar cache para aplicação dinâmica
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        
        proxy_redirect off;
        proxy_buffering off;
    }

    # Servir arquivos estáticos diretamente (melhor performance)
    location /static/ {
        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Servir arquivos de mídia diretamente
    location /media/ {
        alias /home/institutoacquaor/public_html/rh-acqua/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Logs específicos para debug
    access_log /var/log/nginx/rh.institutoacqua.access.log;
    error_log /var/log/nginx/rh.institutoacqua.error.log;
}
EOF

echo "✅ Configuração criada em /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf"

# Testar configuração nginx
echo "🔍 Testando configuração do nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx válida"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso"
        
        # Testar se Django está respondendo
        echo "🔍 Testando aplicação Django..."
        DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
        
        if [ "$DJANGO_STATUS" = "302" ] || [ "$DJANGO_STATUS" = "200" ]; then
            echo "✅ Django respondendo na porta 8000 (status: $DJANGO_STATUS)"
            
            # Testar domínio
            echo "🔍 Testando domínio rh.institutoacqua.org.br..."
            sleep 2
            DOMAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/)
            
            if [ "$DOMAIN_STATUS" = "302" ] || [ "$DOMAIN_STATUS" = "200" ]; then
                echo "🎉 SUCESSO! Domínio funcionando (status: $DOMAIN_STATUS)"
                echo ""
                echo "✅ Configuração concluída com sucesso!"
                echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
            else
                echo "⚠️  Domínio ainda não funcionando (status: $DOMAIN_STATUS)"
                echo "Aguarde alguns minutos para propagação DNS"
            fi
        else
            echo "❌ Django não está respondendo na porta 8000 (status: $DJANGO_STATUS)"
            echo "Verifique se a aplicação Docker está rodando"
        fi
    else
        echo "❌ Erro ao recarregar nginx"
        echo "Verifique os logs: journalctl -u nginx"
    fi
else
    echo "❌ Erro na configuração nginx"
    echo "Verifique o arquivo criado e execute: nginx -t"
fi

echo ""
echo "=== Configuração finalizada ==="
echo "📁 Backup salvo em: /etc/nginx/conf.d/users/institutoacquaor.conf.backup.*"
echo "📝 Nova configuração: /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf"
echo "📋 Logs nginx: /var/log/nginx/rh.institutoacqua.*.log"
