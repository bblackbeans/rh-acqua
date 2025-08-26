#!/bin/bash

echo "�� Configurando ambiente de desenvolvimento..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose down

# Construir e iniciar containers
echo "🔨 Construindo e iniciando containers..."
docker compose up --build -d

# Aguardar o banco estar pronto
echo "⏳ Aguardando banco de dados estar pronto..."
sleep 10

# Executar migrações
echo "📊 Executando migrações..."
docker compose exec web python manage.py migrate

# Criar superusuário
echo "👤 Criando superusuário..."
docker compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker compose exec web python manage.py collectstatic --noinput

echo "✅ Setup concluído!"
echo "🌐 Aplicação disponível em: http://localhost:8000"
echo "📊 Admin disponível em: http://localhost:8000/admin"
echo ""
echo "Para parar os containers: docker compose down"
echo "Para ver logs: docker compose logs -f"
echo "Para acessar o container: docker compose exec web bash"
