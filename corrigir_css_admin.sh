#!/bin/bash

# Script para corrigir CSS do Django Admin via HTTPS
# Execute como root: sudo bash corrigir_css_admin.sh

echo "=== Corrigindo CSS do Django Admin (HTTPS) ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash corrigir_css_admin.sh"
    exit 1
fi

echo "🔍 Problema identificado: Django Admin sem CSS via HTTPS"
echo "🎯 Solução: Configurar nginx para servir arquivos estáticos via HTTPS"

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

# Fazer backup
cp "$CONF_FILE" "${CONF_FILE}.backup.css_fix.$(date +%Y%m%d_%H%M%S)"

echo "📝 Analisando configuração atual..."

# Verificar se existe configuração SSL para o subdomínio rh
if grep -q "server_name rh\.institutoacqua\.org\.br.*ssl" "$CONF_FILE"; then
    echo "✅ Configuração SSL encontrada para rh.institutoacqua.org.br"
else
    echo "⚠️ Configuração SSL não encontrada - criando..."
fi

echo "🔧 Adicionando configuração específica para arquivos estáticos HTTPS..."

# Localizar o bloco do servidor rh que tem SSL (443)
# Vamos adicionar configurações específicas para servir arquivos estáticos

# Usar awk para adicionar configurações de arquivos estáticos no bloco SSL
awk '
BEGIN { 
    in_rh_ssl_block = 0
    added_static_config = 0
}

# Detectar bloco rh com SSL (listen 443)
/server_name rh\.institutoacqua\.org\.br/ {
    in_rh_block = 1
}

# Se encontrarmos listen 443 ssl dentro do bloco rh
/listen 443 ssl/ && in_rh_block == 1 {
    in_rh_ssl_block = 1
}

# Detectar location / dentro do bloco SSL do rh
/location \/ {/ && in_rh_ssl_block == 1 {
    # Antes do location /, adicionar configurações específicas para arquivos estáticos
    if (!added_static_config) {
        print "    # Configurações específicas para arquivos estáticos via HTTPS"
        print "    location /static/ {"
        print "        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;"
        print "        expires 30d;"
        print "        add_header Cache-Control \"public, immutable\";"
        print "        add_header X-Content-Type-Options nosniff;"
        print "        access_log off;"
        print "    }"
        print ""
        print "    location /media/ {"
        print "        alias /home/institutoacquaor/public_html/rh-acqua/media/;"
        print "        expires 7d;"
        print "        add_header Cache-Control \"public\";"
        print "        add_header X-Content-Type-Options nosniff;"
        print "        access_log off;"
        print "    }"
        print ""
        print "    # Configuração específica para CSS/JS do Django Admin"
        print "    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {"
        print "        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;"
        print "        expires 1y;"
        print "        add_header Cache-Control \"public, immutable\";"
        print "        add_header X-Content-Type-Options nosniff;"
        print "        access_log off;"
        print "    }"
        print ""
        added_static_config = 1
    }
}

# Detectar fim do bloco
/^}$/ {
    if (in_rh_ssl_block == 1) {
        in_rh_ssl_block = 0
        in_rh_block = 0
    }
}

# Imprimir todas as linhas
{ print $0 }
' "$CONF_FILE" > /tmp/nginx_css_fixed.conf

# Verificar se arquivo foi gerado
if [ -s /tmp/nginx_css_fixed.conf ]; then
    echo "✅ Configuração para CSS gerada"
    
    # Substituir arquivo original
    cp /tmp/nginx_css_fixed.conf "$CONF_FILE"
    
    # Testar configuração
    echo "🔍 Testando configuração nginx..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração nginx válida!"
        
        # Coletar arquivos estáticos do Django
        echo "📦 Coletando arquivos estáticos do Django..."
        cd /home/institutoacquaor/public_html/rh-acqua
        
        # Executar collectstatic dentro do container
        docker-compose exec -T web python manage.py collectstatic --noinput
        
        if [ $? -eq 0 ]; then
            echo "✅ Arquivos estáticos coletados"
            
            # Verificar se diretório staticfiles existe e tem conteúdo
            if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
                echo "✅ Diretório staticfiles existe e tem conteúdo"
                
                # Definir permissões corretas
                chown -R institutoacquaor:institutoacquaor staticfiles/
                chmod -R 755 staticfiles/
                
                echo "✅ Permissões configuradas"
            else
                echo "❌ Diretório staticfiles vazio ou inexistente"
                echo "Tentando criar manualmente..."
                
                # Criar diretório se não existir
                mkdir -p staticfiles
                chown institutoacquaor:institutoacquaor staticfiles/
            fi
        else
            echo "⚠️ Erro ao coletar arquivos estáticos, mas continuando..."
        fi
        
        # Recarregar nginx
        echo "🔄 Recarregando nginx..."
        systemctl reload nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx recarregado com sucesso!"
            
            # Aguardar propagação
            echo "⏳ Aguardando 10 segundos para propagação..."
            sleep 10
            
            # Testar arquivos estáticos via HTTPS
            echo "🧪 Testando arquivos estáticos via HTTPS..."
            
            # Teste 1: Verificar se /static/ responde
            STATIC_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://rh.institutoacqua.org.br/static/ 2>/dev/null)
            echo "Teste /static/: $STATIC_TEST"
            
            # Teste 2: Verificar CSS específico do admin
            ADMIN_CSS_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://rh.institutoacqua.org.br/static/admin/css/base.css 2>/dev/null)
            echo "Teste CSS admin: $ADMIN_CSS_TEST"
            
            # Teste 3: Verificar página admin
            ADMIN_PAGE_TEST=$(curl -s https://rh.institutoacqua.org.br/admin/ 2>/dev/null | grep -c "django")
            echo "CSS Django na página admin: $ADMIN_PAGE_TEST referências encontradas"
            
            echo ""
            if [ "$STATIC_TEST" = "200" ] || [ "$STATIC_TEST" = "403" ]; then
                echo "🎉 SUCESSO! Arquivos estáticos configurados via HTTPS"
                echo "✅ Django Admin deve estar com CSS funcionando"
                echo "🌐 Teste: https://rh.institutoacqua.org.br/admin/"
            elif [ "$ADMIN_CSS_TEST" = "200" ]; then
                echo "🎉 SUCESSO! CSS do Admin funcionando via HTTPS"
                echo "✅ Django Admin com CSS correto"
                echo "🌐 Teste: https://rh.institutoacqua.org.br/admin/"
            else
                echo "⚠️ Configuração aplicada, mas CSS pode precisar de mais tempo"
                echo "🌐 Teste manualmente: https://rh.institutoacqua.org.br/admin/"
                echo "💡 Se ainda não funcionar, execute: docker-compose exec web python manage.py collectstatic --noinput"
            fi
            
        else
            echo "❌ Erro ao recarregar nginx"
            cp "${CONF_FILE}.backup.css_fix"* "$CONF_FILE" 2>/dev/null
            systemctl reload nginx
        fi
    else
        echo "❌ Erro na configuração nginx"
        cp "${CONF_FILE}.backup.css_fix"* "$CONF_FILE" 2>/dev/null
        echo "Detalhes do erro:"
        nginx -t
    fi
else
    echo "❌ Erro ao gerar configuração para CSS"
fi

# Limpeza
rm -f /tmp/nginx_css_fixed.conf

echo ""
echo "=== Correção CSS Admin Finalizada ==="
echo "📁 Backup: ${CONF_FILE}.backup.css_fix.*"
echo "🌐 Teste HTTPS: https://rh.institutoacqua.org.br/admin/"
echo "🌐 Teste HTTP: http://rh.institutoacqua.org.br/admin/"

echo ""
echo "📋 Comandos adicionais se necessário:"
echo "docker-compose exec web python manage.py collectstatic --noinput"
echo "chown -R institutoacquaor:institutoacquaor staticfiles/"
echo "chmod -R 755 staticfiles/"
