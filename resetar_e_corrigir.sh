#!/bin/bash

# Script para resetar configuração e aplicar correção limpa
# Execute como root: sudo bash resetar_e_corrigir.sh

echo "=== Resetar e Corrigir Nginx (Método Limpo) ==="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo bash resetar_e_corrigir.sh"
    exit 1
fi

CONF_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf"

# Usar o backup mais antigo (original)
BACKUP_FILE="/etc/nginx/conf.d/users/institutoacquaor.conf.backup.20250905_163641"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup original não encontrado"
    echo "Listando backups disponíveis:"
    ls -la "${CONF_FILE}.backup"* | head -5
    exit 1
fi

echo "🔄 Restaurando configuração original..."
cp "$BACKUP_FILE" "$CONF_FILE"

echo "✅ Configuração original restaurada"

# Agora aplicar uma correção muito simples e limpa
echo "🎯 Aplicando correção limpa (apenas mudança de proxy_pass)..."

# Fazer backup da restauração
cp "$CONF_FILE" "${CONF_FILE}.antes_correcao.$(date +%Y%m%d_%H%M%S)"

# Substituição simples: trocar apenas a variável do proxy_pass
sed -i 's|\$CPANEL_APACHE_PROXY_PASS|http://127.0.0.1:8000|g' "$CONF_FILE"

echo "✅ Correção aplicada - substituindo variável por URL direta"

# Testar configuração
echo "🔍 Testando configuração..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx válida!"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso!"
        
        # Aguardar um pouco para propagação
        echo "⏳ Aguardando propagação (10 segundos)..."
        sleep 10
        
        # Teste múltiplo
        echo "🔍 Testando domínio..."
        
        for i in {1..3}; do
            echo "--- Teste $i ---"
            
            RESPONSE=$(curl -s -I http://rh.institutoacqua.org.br/ 2>/dev/null)
            
            if [ -n "$RESPONSE" ]; then
                echo "Resposta recebida:"
                echo "$RESPONSE" | head -3
                
                if echo "$RESPONSE" | grep -q "Server: gunicorn"; then
                    echo ""
                    echo "🎉🎉🎉 SUCESSO TOTAL! 🎉🎉🎉"
                    echo "✅ Django funcionando via rh.institutoacqua.org.br"
                    echo "🌐 Acesse: http://rh.institutoacqua.org.br/"
                    break
                elif echo "$RESPONSE" | grep -q "HTTP.*302"; then
                    echo "✅ Redirecionamento detectado - provavelmente Django!"
                    echo "🌐 Teste no navegador: http://rh.institutoacqua.org.br/"
                    break
                elif echo "$RESPONSE" | grep -q "HTTP.*200"; then
                    echo "⚠️ Resposta 200 - verificar se é Django"
                    
                    # Teste adicional do conteúdo
                    CONTENT_SAMPLE=$(curl -s http://rh.institutoacqua.org.br/ 2>/dev/null | head -c 200)
                    if echo "$CONTENT_SAMPLE" | grep -qi "django\|rh\|login\|html\|<!"; then
                        echo "✅ Conteúdo parece ser Django!"
                        break
                    fi
                fi
            else
                echo "❌ Sem resposta"
            fi
            
            if [ $i -lt 3 ]; then
                echo "Aguardando 5s para próximo teste..."
                sleep 5
            fi
        done
        
        echo ""
        echo "📋 Status final:"
        echo "- Django local (127.0.0.1:8000): $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null)"
        echo "- Domínio rh.institutoacqua.org.br: $(curl -s -o /dev/null -w "%{http_code}" http://rh.institutoacqua.org.br/ 2>/dev/null)"
        
    else
        echo "❌ Erro ao recarregar nginx"
        echo "Restaurando configuração original..."
        cp "$BACKUP_FILE" "$CONF_FILE"
        systemctl reload nginx
    fi
else
    echo "❌ Erro na configuração nginx"
    echo "Restaurando configuração original..."
    cp "$BACKUP_FILE" "$CONF_FILE"
    echo "Detalhes do erro:"
    nginx -t
fi

echo ""
echo "=== Reset e Correção Finalizada ==="
echo "📁 Backup original usado: $BACKUP_FILE"
echo "🌐 Teste final: http://rh.institutoacqua.org.br/"
