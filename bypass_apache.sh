#!/bin/bash

# Script para bypass do Apache - nginx direto para Django
# Execute como root: sudo bash bypass_apache.sh

echo "=== Bypass do Apache - Nginx Direto para Django ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash bypass_apache.sh"
    exit 1
fi

echo "🔍 Problema identificado: nginx → Apache → erro 500"
echo "🎯 Solução: configurar nginx para ir direto ao Django, sem Apache"

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.bypass.$(date +%Y%m%d_%H%M%S)"

echo "📝 Criando configuração de bypass do Apache..."

# Localizar o bloco do servidor rh
START_LINE=$(grep -n "server_name rh\.institutoacqua\.org\.br" "$CONF_FILE" | cut -d: -f1)
echo "Bloco rh inicia na linha: $START_LINE"

# Encontrar fim do bloco
END_LINE=$(tail -n +$START_LINE "$CONF_FILE" | grep -n "^}" | head -1 | cut -d: -f1)
END_LINE=$((START_LINE + END_LINE - 1))
echo "Bloco rh termina na linha: $END_LINE"

# Criar nova configuração que substitui todo o bloco location /
cat > /tmp/new_rh_config << 'EOF'
    # Configuração de bypass do Apache - nginx direto para Django
    location / {
        # Proxy direto para Django
        proxy_pass http://127.0.0.1:8000;
        
        # Headers essenciais
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Configurações de conexão
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
        proxy_request_buffering off;
        
        # Desabilitar completamente o cache
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        
        # Configurações adicionais
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Servir arquivos estáticos diretamente
    location /static/ {
        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;
        expires 1d;
        add_header Cache-Control "public";
        access_log off;
    }

    location /media/ {
        alias /home/institutoacquaor/public_html/rh-acqua/media/;
        expires 1d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Bloquear acesso a arquivos sensíveis
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
EOF

echo "🔧 Aplicando configuração de bypass..."

# Usar awk para substituir todo o bloco location / dentro do servidor rh
awk -v start=$START_LINE -v end=$END_LINE '
BEGIN { 
    in_rh_block = 0
    in_location_block = 0
    location_replaced = 0
}

# Detectar início do bloco rh
NR == start { in_rh_block = 1 }

# Detectar fim do bloco rh
NR == end { 
    in_rh_block = 0
    # Se estamos saindo do bloco e não substituímos o location, adicionar antes de fechar
    if (in_rh_block && !location_replaced) {
        # Adicionar nova configuração
        while ((getline line < "/tmp/new_rh_config") > 0) {
            print line
        }
        close("/tmp/new_rh_config")
        location_replaced = 1
    }
}

# Dentro do bloco rh
{
    if (in_rh_block == 1) {
        # Detectar início do location /
        if (/location \/ {/ && !location_replaced) {
            in_location_block = 1
            # Adicionar nova configuração em vez do location antigo
            while ((getline line < "/tmp/new_rh_config") > 0) {
                print line
            }
            close("/tmp/new_rh_config")
            location_replaced = 1
            next
        }
        
        # Pular linhas do location / antigo
        if (in_location_block == 1) {
            if (/^    }$/) {
                in_location_block = 0
            }
            next
        }
        
        # Pular outras configurações de proxy/cache problemáticas
        if (/include conf\.d\/includes-optional\/cpanel-proxy\.conf/ ||
            /proxy_pass \$CPANEL_APACHE_PROXY_PASS/ ||
            /proxy_cache/ ||
            /proxy_no_cache/ ||
            /proxy_cache_bypass/) {
            next
        }
    }
    
    print $0
}
' "$CONF_FILE" > /tmp/nginx_bypass.conf

# Verificar se arquivo foi gerado
if [ -s /tmp/nginx_bypass.conf ]; then
    echo "✅ Configuração de bypass gerada"
    
    # Substituir arquivo original
    cp /tmp/nginx_bypass.conf "$CONF_FILE"
    
    # Testar configuração
    echo "🔍 Testando configuração de bypass..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração nginx válida!"
        
        # Recarregar nginx
        echo "🔄 Recarregando nginx..."
        systemctl reload nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx recarregado com bypass ativo!"
            
            # Aguardar estabilização
            echo "⏳ Aguardando 15 segundos para estabilização..."
            sleep 15
            
            # Testes intensivos
            echo "🧪 Testes intensivos do bypass..."
            
            for i in {1..6}; do
                echo "--- Teste intensivo $i/6 ---"
                
                # Teste com timeout maior
                RESPONSE=$(timeout 10 curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
                
                if [ -n "$RESPONSE" ]; then
                    STATUS=$(echo "$RESPONSE" | head -1 | tr -d '\r')
                    SERVER_HEADER=$(echo "$RESPONSE" | grep -i "server:" | tr -d '\r')
                    
                    echo "Status: $STATUS"
                    echo "$SERVER_HEADER"
                    
                    if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                        echo ""
                        echo "🎉🎉🎉 SUCESSO ABSOLUTO! 🎉🎉🎉"
                        echo "✅ BYPASS FUNCIONOU! Nginx → Django direto"
                        echo "🚀 Apache foi contornado com sucesso!"
                        echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
                        break
                        
                    elif echo "$RESPONSE" | grep -q "302\|301"; then
                        echo "🎉 SUCESSO! Redirecionamento Django via bypass"
                        echo "✅ Nginx → Django funcionando!"
                        break
                        
                    elif echo "$RESPONSE" | grep -q "200"; then
                        echo "✅ Resposta 200 - testando conteúdo..."
                        
                        CONTENT=$(timeout 10 curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 1000)
                        if echo "$CONTENT" | grep -qi "RH\|Django\|login\|form\|html\|doctype\|csrf"; then
                            echo "🎉 SUCESSO! Conteúdo Django detectado via bypass!"
                            break
                        else
                            echo "⚠️ Conteúdo ainda não é Django"
                        fi
                        
                    elif echo "$RESPONSE" | grep -q "500"; then
                        echo "❌ Ainda erro 500 - problema mais profundo"
                        
                    elif echo "$RESPONSE" | grep -q "502\|503\|504"; then
                        echo "⚠️ Erro de gateway - Django pode estar temporariamente indisponível"
                        
                    else
                        echo "❓ Resposta inesperada"
                    fi
                else
                    echo "❌ Timeout ou sem resposta"
                fi
                
                if [ $i -lt 6 ]; then
                    echo "Aguardando 8s..."
                    sleep 8
                fi
            done
            
            echo ""
            echo "📊 Status final após bypass:"
            echo "Django local:  $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
            echo "Via domínio:   $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"
            
        else
            echo "❌ Erro ao recarregar nginx"
            cp "${CONF_FILE}.backup.bypass"* "$CONF_FILE" 2>/dev/null
            systemctl reload nginx
        fi
    else
        echo "❌ Erro na configuração de bypass"
        cp "${CONF_FILE}.backup.bypass"* "$CONF_FILE" 2>/dev/null
        nginx -t
    fi
else
    echo "❌ Erro ao gerar configuração de bypass"
fi

# Limpeza
rm -f /tmp/new_rh_config /tmp/nginx_bypass.conf

echo ""
echo "=== Bypass do Apache Finalizado ==="
echo "📁 Backup: ${CONF_FILE}.backup.bypass.*"
echo "🌐 Teste: http://rh.institutoacqua.org.br/"
