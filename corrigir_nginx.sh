#!/bin/bash

# Script para corrigir a configuração nginx do subdomínio rh
# Execute como root: sudo bash corrigir_nginx.sh

echo "=== Corrigindo configuração nginx para rh.institutoacqua.org.br ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_nginx.sh"
    exit 1
fi

# Remover arquivo incorreto
echo "🗑️ Removendo arquivo incorreto..."
rm -f /etc/nginx/conf.d/users/institutoacquaor/rh_proxy.conf

# Arquivo de configuração principal
CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

echo "📝 Modificando configuração em: $CONF_FILE"

# Fazer backup se ainda não existe
if [ ! -f "${CONF_FILE}.backup" ]; then
    cp "$CONF_FILE" "${CONF_FILE}.backup"
    echo "✅ Backup criado: ${CONF_FILE}.backup"
fi

# Criar script Python para modificar a configuração
cat > /tmp/fix_nginx.py << 'EOF'
import re

# Ler arquivo atual
with open('/etc/nginx/conf.d/users/institutoacquaor.conf', 'r') as f:
    content = f.read()

# Padrão para encontrar o bloco do servidor rh.institutoacqua.org.br
pattern = r'(server\s*{[^}]*server_name\s+rh\.institutoacqua\.org\.br[^}]*?location\s+/\s*{[^}]*?proxy_pass[^}]*?}[^}]*?})'

# Substituição: modificar apenas o location / dentro do servidor rh
replacement_location = '''location / {
        # Proxy para aplicação Django na porta 8000
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        proxy_redirect off;
    }'''

# Encontrar e substituir apenas a seção location / do servidor rh
rh_server_pattern = r'(server\s*{[^{}]*server_name\s+rh\.institutoacqua\.org\.br[^{}]*?)(location\s+/\s*{[^{}]*?})'

def replace_location(match):
    server_start = match.group(1)
    return server_start + replacement_location

# Aplicar substituição
new_content = re.sub(rh_server_pattern, replace_location, content, flags=re.DOTALL)

# Salvar arquivo modificado
with open('/etc/nginx/conf.d/users/institutoacquaor.conf', 'w') as f:
    f.write(new_content)

print("✅ Configuração modificada")
EOF

# Executar script Python
python3 /tmp/fix_nginx.py

# Testar configuração
echo "🔍 Testando configuração..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração válida"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado"
        
        # Aguardar um pouco
        sleep 3
        
        # Testar domínio
        echo "🔍 Testando domínio..."
        RESULT=$(curl -s -I http://rh.institutoacqua.org.br/ | head -1)
        echo "Resultado: $RESULT"
        
        if echo "$RESULT" | grep -q "302\|200"; then
            SERVER=$(curl -s -I http://rh.institutoacqua.org.br/ | grep -i "server:" || echo "Server não encontrado")
            echo "Server header: $SERVER"
            
            if echo "$SERVER" | grep -q "gunicorn"; then
                echo "🎉 SUCESSO! Django funcionando através do domínio"
            else
                echo "⚠️ Domínio responde mas ainda não é Django"
            fi
        else
            echo "❌ Domínio ainda não funcionando corretamente"
        fi
    else
        echo "❌ Erro ao recarregar nginx"
    fi
else
    echo "❌ Erro na configuração"
    echo "Restaurando backup..."
    cp "${CONF_FILE}.backup" "$CONF_FILE"
    systemctl reload nginx
fi

# Limpeza
rm -f /tmp/fix_nginx.py

echo "=== Finalizado ==="
