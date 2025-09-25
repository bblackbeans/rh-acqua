#!/bin/bash

echo "🧪 TESTE DE URLS DE CRIAÇÃO DE VAGA"
echo "==================================="

base_url="https://rh.institutoacqua.org.br"

echo ""
echo "1️⃣ TESTANDO URL CORRETA: /vacancies/vacancy/create/"
echo "=================================================="
response=$(curl -s -o /dev/null -w "%{http_code}" "$base_url/vacancies/vacancy/create/")
echo "Status: $response"

if [ "$response" = "200" ]; then
    echo "✅ URL correta acessível!"
elif [ "$response" = "302" ]; then
    echo "⚠️ Redirecionamento (provavelmente para login)"
elif [ "$response" = "403" ]; then
    echo "❌ Erro 403 - Problema de CSRF ou permissão"
else
    echo "❌ Erro: $response"
fi

echo ""
echo "2️⃣ TESTANDO URL INCORRETA: /vacancies/create/"
echo "============================================="
response=$(curl -s -o /dev/null -w "%{http_code}" "$base_url/vacancies/create/")
echo "Status: $response"

if [ "$response" = "404" ]; then
    echo "✅ Confirmado: URL incorreta retorna 404"
else
    echo "❓ Status inesperado: $response"
fi

echo ""
echo "3️⃣ TESTANDO PÁGINA DE GESTÃO: /vacancies/recruiter/gestao-vagas/"
echo "=============================================================="
response=$(curl -s -o /dev/null -w "%{http_code}" "$base_url/vacancies/recruiter/gestao-vagas/")
echo "Status: $response"

if [ "$response" = "200" ]; then
    echo "✅ Página de gestão acessível"
elif [ "$response" = "302" ]; then
    echo "⚠️ Redirecionamento (provavelmente para login)"
else
    echo "❌ Erro: $response"
fi

echo ""
echo "4️⃣ VERIFICANDO CSRF TOKEN NA URL CORRETA"
echo "======================================="
echo "Buscando CSRF token em $base_url/vacancies/vacancy/create/..."
csrf_token=$(curl -s "$base_url/vacancies/vacancy/create/" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | head -1)

if [ ! -z "$csrf_token" ]; then
    echo "✅ CSRF token encontrado: $csrf_token"
else
    echo "❌ CSRF token não encontrado"
fi

echo ""
echo "✅ Teste concluído!"
echo ""
echo "🎯 RESUMO:"
echo "=========="
echo "URL correta para criação de vaga:"
echo "https://rh.institutoacqua.org.br/vacancies/vacancy/create/"
echo ""
echo "URL incorreta (retorna 404):"
echo "https://rh.institutoacqua.org.br/vacancies/create/"
