#!/bin/bash

echo "🔍 VERIFICANDO DADOS DO BANCO PARA FORMULÁRIO"
echo "============================================="

echo ""
echo "1️⃣ VERIFICANDO HOSPITAIS EXISTENTES"
echo "==================================="

echo "Executando: SELECT id, name FROM vacancies_hospital WHERE is_active = true;"
sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c "SELECT id, name FROM vacancies_hospital WHERE is_active = true;"

echo ""
echo "2️⃣ VERIFICANDO DEPARTAMENTOS EXISTENTES"
echo "======================================"

echo "Executando: SELECT id, name, hospital_id FROM vacancies_department WHERE is_active = true;"
sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c "SELECT id, name, hospital_id FROM vacancies_department WHERE is_active = true;"

echo ""
echo "3️⃣ VERIFICANDO CATEGORIAS DE VAGA"
echo "================================"

echo "Executando: SELECT id, name FROM vacancies_jobcategory WHERE is_active = true;"
sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c "SELECT id, name FROM vacancies_jobcategory WHERE is_active = true;"

echo ""
echo "4️⃣ VERIFICANDO HABILIDADES"
echo "========================="

echo "Executando: SELECT id, name FROM vacancies_skill WHERE is_active = true;"
sudo docker exec rh-acqua-db-1 psql -U rh_acqua_user -d rh_acqua_db -c "SELECT id, name FROM vacancies_skill WHERE is_active = true;"

echo ""
echo "✅ Verificação concluída!"
echo ""
echo "🎯 USO DOS DADOS:"
echo "Use os IDs retornados acima para testar o formulário"
echo "com dados válidos que existem no banco de dados."


