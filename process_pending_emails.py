#!/usr/bin/env python3
"""
Script para processar emails pendentes após correção do problema SMTP
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/institutoacquaor/public_html/rh-acqua')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from email_system.models import EmailQueue
from email_system.services import EmailQueueService
from django.utils import timezone

def process_pending_emails(limit=50):
    """Processa emails pendentes"""
    print(f"=== PROCESSANDO ATÉ {limit} EMAILS PENDENTES ===")
    
    # Buscar emails pendentes
    pending_emails = EmailQueue.objects.filter(
        status='pending',
        scheduled_at__lte=timezone.now()
    ).order_by('-priority', 'scheduled_at')[:limit]
    
    total = pending_emails.count()
    print(f"Encontrados {total} emails pendentes")
    
    if total == 0:
        print("Nenhum email pendente para processar")
        return
    
    success_count = 0
    error_count = 0
    
    for i, email in enumerate(pending_emails, 1):
        print(f"\n[{i}/{total}] Processando email ID {email.id}")
        print(f"Para: {email.to_email}")
        print(f"Assunto: {email.subject}")
        
        try:
            result = EmailQueueService.process_queue_item(email)
            
            if result:
                success_count += 1
                print("✅ Sucesso")
            else:
                error_count += 1
                print(f"❌ Falha: {email.error_message}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Erro: {e}")
    
    print(f"\n=== RESULTADO ===")
    print(f"Total processados: {total}")
    print(f"Sucessos: {success_count}")
    print(f"Falhas: {error_count}")
    print(f"Taxa de sucesso: {(success_count/total)*100:.1f}%")

def retry_failed_emails(limit=20):
    """Tenta reenviar emails que falharam"""
    print(f"\n=== TENTANDO REENVIAR ATÉ {limit} EMAILS FALHADOS ===")
    
    # Buscar emails que podem ser reenviados
    failed_emails = EmailQueue.objects.filter(
        status='failed',
        retry_count__lt=3
    ).order_by('-priority', 'created_at')[:limit]
    
    total = failed_emails.count()
    print(f"Encontrados {total} emails que podem ser reenviados")
    
    if total == 0:
        print("Nenhum email para reenviar")
        return
    
    retried_count = 0
    success_count = 0
    
    for i, email in enumerate(failed_emails, 1):
        print(f"\n[{i}/{total}] Tentando reenviar email ID {email.id}")
        print(f"Para: {email.to_email}")
        print(f"Tentativas anteriores: {email.retry_count}")
        
        try:
            # Marcar como pendente para reenvio
            email.status = 'pending'
            email.scheduled_at = timezone.now()
            email.save()
            retried_count += 1
            
            # Processar imediatamente
            result = EmailQueueService.process_queue_item(email)
            
            if result:
                success_count += 1
                print("✅ Reenviado com sucesso")
            else:
                print(f"❌ Falha no reenvio: {email.error_message}")
                
        except Exception as e:
            print(f"❌ Erro no reenvio: {e}")
    
    print(f"\n=== RESULTADO DO REENVIO ===")
    print(f"Emails marcados para reenvio: {retried_count}")
    print(f"Reenviados com sucesso: {success_count}")
    if retried_count > 0:
        print(f"Taxa de sucesso: {(success_count/retried_count)*100:.1f}%")

def show_email_stats():
    """Mostra estatísticas dos emails"""
    print("\n=== ESTATÍSTICAS ATUAIS ===")
    
    from django.db.models import Count
    
    stats = EmailQueue.objects.values('status').annotate(count=Count('id'))
    
    for stat in stats:
        status = stat['status']
        count = stat['count']
        print(f"{status}: {count}")
    
    total = sum(stat['count'] for stat in stats)
    print(f"Total: {total}")
    
    # Emails recentes
    recent_failed = EmailQueue.objects.filter(
        status='failed',
        created_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    
    recent_pending = EmailQueue.objects.filter(
        status='pending',
        created_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    
    print(f"\nÚltimas 24h:")
    print(f"Falhados: {recent_failed}")
    print(f"Pendentes: {recent_pending}")

def main():
    print("=== SCRIPT DE PROCESSAMENTO DE EMAILS ===")
    
    # Mostrar estatísticas
    show_email_stats()
    
    # Processar emails pendentes
    process_pending_emails(limit=50)
    
    # Tentar reenviar emails falhados
    retry_failed_emails(limit=20)
    
    # Mostrar estatísticas finais
    show_email_stats()
    
    print("\n=== SCRIPT CONCLUÍDO ===")
    print("Verifique o Django Admin para mais detalhes")

if __name__ == "__main__":
    main()


