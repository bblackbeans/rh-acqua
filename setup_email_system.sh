#!/bin/bash

# Script de configuração do Sistema de Email - RH Acqua
# Este script configura o sistema de email com configurações básicas

echo "🚀 Configurando Sistema de Email - RH Acqua"
echo "=============================================="

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python3 não encontrado"
    exit 1
fi

echo "✅ Ambiente verificado"

# Aplicar migrações
echo "📦 Aplicando migrações..."
python3 manage.py migrate email_system

if [ $? -eq 0 ]; then
    echo "✅ Migrações aplicadas com sucesso"
else
    echo "❌ Erro ao aplicar migrações"
    exit 1
fi

# Criar templates padrão
echo "📝 Criando templates de email padrão..."
python3 manage.py create_default_email_templates

if [ $? -eq 0 ]; then
    echo "✅ Templates criados com sucesso"
else
    echo "❌ Erro ao criar templates"
    exit 1
fi

# Solicitar configurações SMTP
echo ""
echo "📧 Configuração SMTP"
echo "===================="
echo "Para configurar o sistema de email, você precisa fornecer:"
echo ""

read -p "Servidor SMTP (padrão: smtp.gmail.com): " SMTP_HOST
SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}

read -p "Porta SMTP (padrão: 587): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "Usuário SMTP: " SMTP_USERNAME
if [ -z "$SMTP_USERNAME" ]; then
    echo "❌ Usuário SMTP é obrigatório"
    exit 1
fi

read -s -p "Senha SMTP: " SMTP_PASSWORD
echo ""
if [ -z "$SMTP_PASSWORD" ]; then
    echo "❌ Senha SMTP é obrigatória"
    exit 1
fi

read -p "Email remetente: " FROM_EMAIL
if [ -z "$FROM_EMAIL" ]; then
    echo "❌ Email remetente é obrigatório"
    exit 1
fi

read -p "Nome do remetente (padrão: RH Acqua): " FROM_NAME
FROM_NAME=${FROM_NAME:-RH Acqua}

# Criar configuração SMTP
echo "⚙️ Criando configuração SMTP..."
python3 manage.py create_default_smtp_config \
    --host "$SMTP_HOST" \
    --port "$SMTP_PORT" \
    --username "$SMTP_USERNAME" \
    --password "$SMTP_PASSWORD" \
    --from-email "$FROM_EMAIL" \
    --from-name "$FROM_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Configuração SMTP criada com sucesso"
else
    echo "❌ Erro ao criar configuração SMTP"
    exit 1
fi

# Testar processamento da fila
echo "🧪 Testando processamento da fila..."
python3 manage.py process_email_queue --limit 5

if [ $? -eq 0 ]; then
    echo "✅ Processamento da fila funcionando"
else
    echo "⚠️ Aviso: Problema no processamento da fila (pode ser normal se não houver emails)"
fi

echo ""
echo "🎉 Sistema de Email configurado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Acesse o dashboard: /email-system/"
echo "2. Configure templates adicionais em: /admin/email_system/"
echo "3. Configure um cron job para processar emails automaticamente:"
echo "   */5 * * * * cd $(pwd) && python3 manage.py process_email_queue --limit 20"
echo ""
echo "📚 Documentação completa: SISTEMA_EMAIL_README.md"
echo ""
echo "🔧 Comandos úteis:"
echo "- Processar fila: python3 manage.py process_email_queue"
echo "- Testar email: python3 manage.py shell (use EmailTriggerService)"
echo "- Ver logs: /email-system/logs/"
echo ""
echo "✨ Sistema pronto para uso!"
