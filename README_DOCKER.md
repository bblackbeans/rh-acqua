# RH Acqua - Docker Setup

Este projeto foi configurado para rodar com Docker e PostgreSQL.

## 🚀 Início Rápido

### Pré-requisitos
- Docker
- Docker Compose

### Desenvolvimento Local

1. **Clone o repositório e configure o ambiente:**
```bash
# Configurar variáveis de ambiente
cp .env.example .env

# Executar setup automático
./setup.sh
```

2. **Ou execute manualmente:**
```bash
# Construir e iniciar containers
docker compose up --build -d

# Executar migrações
docker compose exec web python manage.py migrate

# Criar superusuário
docker compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker compose exec web python manage.py collectstatic --noinput
```

### Acessar a aplicação
- **Aplicação:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

## 🐳 Comandos Docker Úteis

```bash
# Ver logs
docker compose logs -f

# Parar containers
docker compose down

# Reiniciar containers
docker compose restart

# Acessar container web
docker compose exec web bash

# Executar comandos Django
docker compose exec web python manage.py [comando]

# Ver status dos containers
docker compose ps
```

## 📊 Migração de Dados

Se você tem dados no SQLite e quer migrar para PostgreSQL:

```bash
# Fazer backup dos dados atuais
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -o backup_data.json

# Executar migração
python migrate_to_postgres.py
```

## 🚀 Deploy em Produção

1. **Configure as variáveis de ambiente:**
```bash
cp .env.production .env
# Edite o arquivo .env com suas configurações
```

2. **Execute o deploy:**
```bash
docker compose -f docker compose.prod.yml up --build -d
```

## 🔧 Estrutura dos Containers

- **web:** Aplicação Django
- **db:** PostgreSQL
- **redis:** Redis para cache e Celery
- **celery:** Worker do Celery
- **celery-beat:** Scheduler do Celery

## 📁 Volumes

- `postgres_data`: Dados do PostgreSQL
- `static_volume`: Arquivos estáticos
- `media_volume`: Arquivos de mídia

## 🔒 Segurança

Para produção, certifique-se de:
- Alterar a SECRET_KEY
- Configurar ALLOWED_HOSTS
- Usar senhas seguras
- Configurar HTTPS (recomendado usar Caddy ou Nginx)

## 🆘 Troubleshooting

### Container não inicia
```bash
# Ver logs
docker compose logs web

# Verificar se o banco está rodando
docker compose exec db pg_isready -U rh_acqua_user -d rh_acqua_db
```

### Problemas de permissão
```bash
# Reconstruir containers
docker compose down
docker compose up --build -d
```

### Reset completo
```bash
# Parar e remover tudo
docker compose down -v
docker system prune -f

# Reconstruir
docker compose up --build -d
```
