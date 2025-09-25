#!/bin/bash

# Script para verificar e processar a fila de emails
# Executado pelo crontab a cada 5 minutos

LOG_FILE="/home/institutoacquaor/public_html/rh-acqua/logs/email_queue.log"
PROJECT_DIR="/home/institutoacquaor/public_html/rh-acqua"

# Função para log (apenas warnings e erros)
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Mudar para o diretório do projeto
cd "$PROJECT_DIR"

# Verificar se há emails pendentes
PENDING_COUNT=$(python3 manage.py shell -c "
from email_system.models import EmailQueue
print(EmailQueue.objects.filter(status='pending').count())
" 2>/dev/null)

if [ "$PENDING_COUNT" -gt 0 ]; then
    log_message "Processando $PENDING_COUNT emails pendentes"
    
    # Processar emails
    python3 manage.py process_email_queue --limit 20 >> "$LOG_FILE" 2>&1
    
    # Verificar resultado
    PROCESSED_COUNT=$(python3 manage.py shell -c "
from email_system.models import EmailQueue
print(EmailQueue.objects.filter(status='pending').count())
" 2>/dev/null)
    
    log_message "Emails restantes: $PROCESSED_COUNT"
else
    log_message "Nenhum email pendente"
fi
