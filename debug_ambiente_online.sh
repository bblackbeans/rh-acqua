#!/bin/bash

echo "🔍 DEBUG DE PROBLEMAS DE AMBIENTE ONLINE"
echo "======================================="

echo ""
echo "1️⃣ VERIFICANDO DIFERENÇAS DE CONFIGURAÇÃO"
echo "========================================"

echo "📋 Configurações do Django:"
echo "DEBUG: $(grep DEBUG .env)"
echo "ALLOWED_HOSTS: $(grep ALLOWED_HOSTS .env)"
echo "CSRF_TRUSTED_ORIGINS: $(grep CSRF_TRUSTED_ORIGINS .env)"

echo ""
echo "2️⃣ VERIFICANDO CONTAINER E RECURSOS"
echo "=================================="

echo "📋 Status do container web:"
sudo docker ps --filter 'name=rh-acqua-web-1' --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📋 Uso de memória do container:"
sudo docker stats rh-acqua-web-1 --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "3️⃣ VERIFICANDO LOGS EM TEMPO REAL"
echo "================================"

echo "📋 Logs recentes do container web:"
sudo docker logs rh-acqua-web-1 --tail 20

echo ""
echo "4️⃣ TESTANDO CONECTIVIDADE INTERNA"
echo "================================"

echo "📋 Testando conectividade interna do container:"
sudo docker exec rh-acqua-web-1 curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/

echo ""
echo "5️⃣ VERIFICANDO PERMISSÕES E ARQUIVOS"
echo "==================================="

echo "📋 Verificando permissões do diretório:"
ls -la /home/institutoacquaor/public_html/rh-acqua/ | head -10

echo ""
echo "📋 Verificando se há arquivos de lock ou temporários:"
find /home/institutoacquaor/public_html/rh-acqua/ -name "*.lock" -o -name "*.tmp" -o -name "*.pid" 2>/dev/null

echo ""
echo "6️⃣ VERIFICANDO BANCO DE DADOS"
echo "============================"

echo "📋 Testando conexão com banco:"
sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c "SELECT COUNT(*) FROM vacancies_vacancy;" 2>/dev/null

echo ""
echo "7️⃣ POSSÍVEIS CAUSAS DE AMBIENTE"
echo "=============================="

echo "🔍 Baseado na análise, as possíveis causas são:"
echo ""
echo "1. ❌ Problema de memória/recursos do container"
echo "2. ❌ Timeout na requisição (muito lenta)"
echo "3. ❌ Problema de permissões de arquivo"
echo "4. ❌ Problema de configuração do nginx"
echo "5. ❌ Problema de sessão/cookies"
echo "6. ❌ Problema de cache do Django"
echo "7. ❌ Problema de middleware"
echo "8. ❌ Problema de banco de dados (lentidão)"

echo ""
echo "8️⃣ COMANDOS PARA TESTE ADICIONAL"
echo "==============================="

echo "Execute estes comandos para investigar mais:"
echo ""
echo "# Ver logs em tempo real enquanto testa"
echo "sudo docker logs -f rh-acqua-web-1"
echo ""
echo "# Verificar uso de recursos"
echo "sudo docker stats rh-acqua-web-1"
echo ""
echo "# Testar conectividade interna"
echo "sudo docker exec rh-acqua-web-1 curl -v http://localhost:8000/vacancies/vacancy/create/"
echo ""
echo "# Verificar se há processos travados"
echo "sudo docker exec rh-acqua-web-1 ps aux"

echo ""
echo "✅ Análise de ambiente concluída!"


