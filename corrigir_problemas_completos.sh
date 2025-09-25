#!/bin/bash

echo "🔧 CORRIGINDO TODOS OS PROBLEMAS IDENTIFICADOS"
echo "=============================================="

echo ""
echo "1️⃣ CORRIGINDO CSRF_TRUSTED_ORIGINS"
echo "=================================="

# Verificar configuração atual
echo "📋 Configuração atual:"
grep "CSRF_TRUSTED_ORIGINS" .env

# Corrigir CSRF_TRUSTED_ORIGINS
echo ""
echo "🔐 Corrigindo CSRF_TRUSTED_ORIGINS..."

# Remover linha atual se existir
sed -i '/^CSRF_TRUSTED_ORIGINS=/d' .env

# Adicionar configuração correta
echo "CSRF_TRUSTED_ORIGINS=https://rh.institutoacqua.org.br,http://rh.institutoacqua.org.br,https://158.220.108.114:8000,http://158.220.108.114:8000,http://localhost:8000,http://127.0.0.1:8000" >> .env

echo "✅ CSRF_TRUSTED_ORIGINS corrigido"

echo ""
echo "2️⃣ VERIFICANDO PADRÕES DE URL"
echo "============================="

# Verificar se o arquivo urls.py existe e tem as rotas corretas
if [ -f "vacancies/urls.py" ]; then
    echo "✅ Arquivo vacancies/urls.py encontrado"
    echo "📋 Verificando rotas de criação de vaga..."
    
    if grep -q "create" vacancies/urls.py; then
        echo "✅ Rota 'create' encontrada em vacancies/urls.py"
    else
        echo "❌ Rota 'create' NÃO encontrada em vacancies/urls.py"
    fi
    
    if grep -q "VacancyCreateView" vacancies/urls.py; then
        echo "✅ VacancyCreateView encontrada em vacancies/urls.py"
    else
        echo "❌ VacancyCreateView NÃO encontrada em vacancies/urls.py"
    fi
else
    echo "❌ Arquivo vacancies/urls.py não encontrado"
fi

echo ""
echo "3️⃣ VERIFICANDO CONFIGURAÇÕES DO DJANGO"
echo "======================================"

# Verificar se DEBUG está True (para ver erros detalhados)
if grep -q "DEBUG=True" .env; then
    echo "✅ DEBUG=True (bom para debug)"
else
    echo "⚠️ DEBUG não está True"
fi

echo ""
echo "4️⃣ VERIFICANDO ARQUIVOS ESTÁTICOS"
echo "================================="

# Verificar se os arquivos estáticos foram coletados
if [ -d "staticfiles" ]; then
    echo "✅ Diretório staticfiles existe"
    if [ -f "staticfiles/img/favicon.ico" ]; then
        echo "✅ favicon.ico existe"
    else
        echo "❌ favicon.ico não existe (pode causar erros 404)"
    fi
else
    echo "❌ Diretório staticfiles não existe"
fi

echo ""
echo "5️⃣ COMANDOS PARA EXECUTAR COM SUDO"
echo "=================================="

echo "Execute estes comandos para corrigir os problemas:"
echo ""
echo "# 1. Reiniciar containers para aplicar mudanças de CSRF"
echo "sudo docker-compose restart"
echo ""
echo "# 2. Coletar arquivos estáticos"
echo "sudo docker exec rh-acqua-web-1 python manage.py collectstatic --noinput"
echo ""
echo "# 3. Verificar logs do container após restart"
echo "sudo docker logs rh-acqua-web-1 --tail 20"
echo ""
echo "# 4. Verificar se o container está saudável"
echo "sudo docker ps --filter 'name=rh-acqua-web-1'"
echo ""
echo "# 5. Testar URL correta da criação de vaga"
echo "curl -I https://rh.institutoacqua.org.br/vacancies/vacancy/create/"

echo ""
echo "6️⃣ URLS CORRETAS PARA TESTAR"
echo "============================"

echo "Baseado no erro, a URL correta parece ser:"
echo "✅ https://rh.institutoacqua.org.br/vacancies/vacancy/create/"
echo ""
echo "URLs que retornaram 404:"
echo "❌ https://rh.institutoacqua.org.br/vacancies/create/"

echo ""
echo "✅ Script de correção concluído!"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Execute os comandos sudo acima"
echo "2. Teste a URL correta: /vacancies/vacancy/create/"
echo "3. Verifique se o container fica saudável"
