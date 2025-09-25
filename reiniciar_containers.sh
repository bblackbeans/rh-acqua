#!/bin/bash

echo "🔄 REINICIANDO CONTAINERS DOCKER"
echo "================================="

# Verificar se docker-compose está disponível
if command -v docker-compose &> /dev/null; then
    echo "📦 Usando docker-compose..."
    
    # Listar containers ativos
    echo "📋 Containers ativos antes do restart:"
    docker-compose ps
    
    echo ""
    echo "🔄 Reiniciando containers..."
    sudo docker-compose restart
    
    echo ""
    echo "📋 Containers após o restart:"
    docker-compose ps
    
elif command -v docker &> /dev/null; then
    echo "🐳 Usando docker diretamente..."
    
    # Listar containers relacionados ao projeto
    echo "📋 Containers relacionados ao projeto:"
    docker ps --filter "name=rh-acqua" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "🔄 Reiniciando containers..."
    
    # Reiniciar containers do projeto
    for container in $(docker ps --filter "name=rh-acqua" --format "{{.Names}}"); do
        echo "🔄 Reiniciando $container..."
        sudo docker restart $container
    done
    
    echo ""
    echo "📋 Status após o restart:"
    docker ps --filter "name=rh-acqua" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
else
    echo "❌ Docker não encontrado!"
    exit 1
fi

echo ""
echo "✅ Reinicialização concluída!"
echo ""
echo "🧪 TESTE AGORA:"
echo "==============="
echo "1. Acesse https://rh.institutoacqua.org.br"
echo "2. Faça login como recrutador"
echo "3. Tente criar/editar uma vaga"
echo "4. Verifique se o salvamento funciona"
