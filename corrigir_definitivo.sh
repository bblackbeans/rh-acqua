#!/bin/bash

# Script para correção definitiva - colocar arquivos no local correto
# Execute como root: sudo bash corrigir_definitivo.sh

echo "=== Correção Definitiva do Nginx ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_definitivo.sh"
    exit 1
fi

# O nginx está procurando includes em:
# include conf.d/users/institutoacquaor/rh.institutoacqua.org.br/*.conf;

# Vamos criar o arquivo no local correto
INCLUDE_DIR="/etc/nginx/conf.d/users/institutoacquaor/rh.institutoacqua.org.br"

echo "📁 Criando diretório: $INCLUDE_DIR"
mkdir -p "$INCLUDE_DIR"

# Criar configuração no local que o nginx está procurando
echo "📝 Criando configuração de proxy no local correto..."
cat > "$INCLUDE_DIR/django_proxy.conf" << 'EOF'
# Sobrescrever location / para fazer proxy para Django
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
    proxy_buffering off;
    
    # Desabilitar cache
    proxy_cache off;
    proxy_no_cache 1;
    proxy_cache_bypass 1;
    
    proxy_redirect off;
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
EOF

echo "✅ Configuração criada em: $INCLUDE_DIR/django_proxy.conf"

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
        
        # Aguardar um pouco para propagação
        sleep 5
        
        # Testar domínio
        echo "🔍 Testando domínio rh.institutoacqua.org.br..."
        
        # Teste completo
        RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
        echo "--- Resposta do domínio ---"
        echo "$RESPONSE" | head -5
        
        # Verificar se Django está ativo
        if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
            echo ""
            echo "🎉 SUCESSO TOTAL! Django funcionando via domínio"
            echo "✅ rh.institutoacqua.org.br → Django ativo"
            echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
        elif echo "$RESPONSE" | grep -q "302\|301"; then
            echo ""
            echo "⚠️ Domínio redirecionando (possivelmente Django)"
            echo "Teste diretamente no navegador: http://rh.institutoacqua.org.br/"
        elif echo "$RESPONSE" | grep -q "200"; then
            echo ""
            echo "⚠️ Domínio responde mas verificar no navegador"
            echo "Pode estar funcionando mas headers diferentes"
        else
            echo ""
            echo "❌ Domínio ainda não funcionando corretamente"
        fi
        
        # Teste adicional - verificar conteúdo
        echo ""
        echo "🧪 Teste adicional - verificando conteúdo..."
        CONTENT_TEST=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 100)
        
        if echo "$CONTENT_TEST" | grep -q "RH\|Django\|login\|HTML\|DOCTYPE"; then
            echo "✅ Conteúdo parece ser da aplicação Django"
        else
            echo "⚠️ Conteúdo pode ainda ser listagem de arquivos"
        fi
        
    else
        echo "❌ Erro ao recarregar nginx"
        journalctl -u nginx --no-pager -n 5
    fi
else
    echo "❌ Erro na configuração nginx"
    nginx -t
fi

echo ""
echo "=== Correção Definitiva Finalizada ==="
echo "📁 Configuração em: $INCLUDE_DIR/django_proxy.conf"
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
