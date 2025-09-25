"""
Comando para processar a fila de emails
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from email_system.services import EmailQueueService
from email_system.models import EmailQueue
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Processa emails pendentes na fila'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número máximo de emails para processar por vez (padrão: 10)'
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Tenta reenviar emails que falharam'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove logs antigos e emails processados'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        retry_failed = options['retry_failed']
        cleanup = options['cleanup']
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando processamento da fila de emails...')
        )
        
        # Tentar reenviar emails que falharam
        if retry_failed:
            retried_count = EmailQueueService.retry_failed_emails(limit=5)
            if retried_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'{retried_count} emails falhados foram marcados para reenvio.')
                )
        
        # Processar emails pendentes
        pending_emails = EmailQueueService.get_pending_emails(limit=limit)
        
        if not pending_emails:
            self.stdout.write(
                self.style.WARNING('Nenhum email pendente encontrado.')
            )
            return
        
        self.stdout.write(f'Processando {len(pending_emails)} emails...')
        
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        for email_queue in pending_emails:
            try:
                self.stdout.write(f'Processando email {email_queue.id} para {email_queue.to_email}...')
                
                success = EmailQueueService.process_queue_item(email_queue)
                
                if success:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Email {email_queue.id} enviado com sucesso')
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Falha ao enviar email {email_queue.id}')
                    )
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao processar email {email_queue.id}: {e}')
                )
                logger.error(f'Erro ao processar email {email_queue.id}: {e}')
        
        # Limpeza de dados antigos
        if cleanup:
            self.cleanup_old_data()
        
        # Resumo
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProcessamento concluído:\n'
                f'- Emails processados: {processed_count}\n'
                f'- Sucessos: {success_count}\n'
                f'- Falhas: {failed_count}'
            )
        )
    
    def cleanup_old_data(self):
        """Remove dados antigos para manter o banco limpo"""
        from datetime import timedelta
        
        # Remover logs de emails enviados com mais de 30 dias
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_logs = EmailLog.objects.filter(
            status='sent',
            created_at__lt=cutoff_date
        )
        
        logs_count = old_logs.count()
        if logs_count > 0:
            old_logs.delete()
            self.stdout.write(
                self.style.SUCCESS(f'{logs_count} logs antigos foram removidos.')
            )
        
        # Remover emails da fila que foram enviados com mais de 7 dias
        cutoff_date_queue = timezone.now() - timedelta(days=7)
        
        old_queue_items = EmailQueue.objects.filter(
            status='sent',
            sent_at__lt=cutoff_date_queue
        )
        
        queue_count = old_queue_items.count()
        if queue_count > 0:
            old_queue_items.delete()
            self.stdout.write(
                self.style.SUCCESS(f'{queue_count} itens antigos da fila foram removidos.')
            )
