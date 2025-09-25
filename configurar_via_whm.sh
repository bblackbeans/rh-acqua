#!/bin/bash

# Script para configurar nginx via WHM (método oficial)
# Execute como root: sudo bash configurar_via_whm.sh

echo "=== Configurando nginx via WHM (Método Oficial) ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash configurar_via_whm.sh"
    exit 1
fi

echo "✅ Usando WHM para configuração nginx"

# Verificar se WHM está disponível
if [ ! -f "/usr/local/cpanel/bin/whmapi1" ]; then
    echo "❌ WHM não encontrado"
    exit 1
fi

echo "📋 WHM encontrado, criando configuração..."

# Criar arquivo de configuração nginx específico para o subdomínio
NGINX_INCLUDE_DIR="/etc/nginx/conf.d/userdata/std/2_4/institutoacquaor/rh.institutoacqua.org.br"

echo "📁 Criando diretório: $NGINX_INCLUDE_DIR"
mkdir -p "$NGINX_INCLUDE_DIR"

# Criar configuração específica para o subdomínio
cat > "$NGINX_INCLUDE_DIR/rh_django_proxy.conf" << 'EOF'
# Configuração nginx para proxy do Django (via WHM)
# Este arquivo é incluído automaticamente pelo cPanel/WHM

location / {
    # Proxy para aplicação Django na porta 8000
    proxy_pass http://127.0.0.1:8000;
    
    # Headers obrigatórios para proxy
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
    
    # Configurações de timeout e buffer
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    proxy_buffering off;
    
    # Desabilitar cache para aplicação dinâmica
    proxy_cache off;
    proxy_no_cache 1;
    proxy_cache_bypass 1;
    
    proxy_redirect off;
}

# Otimização para arquivos estáticos
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

# Headers de segurança adicionais
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
EOF

echo "✅ Configuração criada em: $NGINX_INCLUDE_DIR/rh_django_proxy.conf"

# Também criar para HTTPS (porta 443)
NGINX_SSL_DIR="/etc/nginx/conf.d/userdata/ssl/2_4/institutoacquaor/rh.institutoacqua.org.br"
mkdir -p "$NGINX_SSL_DIR"
cp "$NGINX_INCLUDE_DIR/rh_django_proxy.conf" "$NGINX_SSL_DIR/rh_django_proxy.conf"

echo "✅ Configuração SSL criada em: $NGINX_SSL_DIR/rh_django_proxy.conf"

# Reconstruir configuração nginx via WHM
echo "🔨 Reconstruindo configuração nginx via WHM..."
/usr/local/cpanel/scripts/rebuildhttpdconf

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx reconstruída"
    
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
            
            # Aguardar propagação
            sleep 5
            
            # Testar aplicação Django
            echo "🔍 Testando aplicação Django..."
            DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
            echo "Django status: $DJANGO_STATUS"
            
            # Testar domínio
            echo "🔍 Testando domínio rh.institutoacqua.org.br..."
            RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/)
            echo "Resposta do domínio:"
            echo "$RESPONSE" | head -5
            
            # Verificar se o servidor mudou para Django
            if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                echo "🎉 SUCESSO! Django funcionando através do domínio"
                echo "✅ rh.institutoacqua.org.br agora aponta para Django"
            elif echo "$RESPONSE" | grep -q "302\|200"; then
                echo "⚠️ Domínio responde mas ainda pode estar no nginx/apache"
                echo "Aguarde alguns minutos para propagação completa"
            else
                echo "❌ Domínio ainda não funcionando"
            fi
            
        else
            echo "❌ Erro ao recarregar nginx"
        fi
    else
        echo "❌ Erro na configuração nginx"
    fi
else
    echo "❌ Erro ao reconstruir configuração nginx"
fi

echo ""
echo "=== Configuração via WHM finalizada ==="
echo "📁 Configurações criadas:"
echo "   - $NGINX_INCLUDE_DIR/rh_django_proxy.conf"
echo "   - $NGINX_SSL_DIR/rh_django_proxy.conf"
echo ""
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
echo "🔒 Teste SSL: https://rh.institutoacqua.org.br/"
echo ""
echo "ℹ️ Esta configuração via WHM é persistente e sobrevive a atualizações"
