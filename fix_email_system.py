#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas no sistema de email
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('/home/institutoacquaor/public_html/rh-acqua')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from email_system.models import EmailQueue, SMTPConfiguration, EmailTrigger
from email_system.services import EmailService, EmailQueueService
from email_system.email_service_fix import FixedEmailService
from django.utils import timezone
from django.db.models import Count

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_smtp_configurations():
    """Verifica todas as configurações SMTP disponíveis"""
    print_header("CONFIGURAÇÕES SMTP DISPONÍVEIS")
    
    configs = SMTPConfiguration.objects.all()
    for config in configs:
        print(f"ID: {config.id}")
        print(f"Nome: {config.name}")
        print(f"Host: {config.host}:{config.port}")
        print(f"Username: {config.username}")
        print(f"From Email: {config.from_email}")
        print(f"Ativo: {config.is_active}")
        print(f"Padrão: {config.is_default}")
        print(f"TLS: {config.use_tls}, SSL: {config.use_ssl}")
        print("-" * 40)

def check_email_status():
    """Verifica o status dos emails na fila"""
    print_header("STATUS DOS EMAILS")
    
    status_counts = EmailQueue.objects.values('status').annotate(count=Count('id'))
    total = 0
    for item in status_counts:
        print(f"{item['status']}: {item['count']}")
        total += item['count']
    
    print(f"\nTotal: {total}")
    
    # Mostrar alguns exemplos de emails falhados
    print_header("EXEMPLOS DE EMAILS FALHADOS")
    failed_emails = EmailQueue.objects.filter(status='failed').order_by('-created_at')[:5]
    for email in failed_emails:
        print(f"ID: {email.id}")
        print(f"Para: {email.to_email}")
        print(f"Assunto: {email.subject}")
        print(f"Erro: {email.error_message}")
        print(f"Tentativas: {email.retry_count}")
        print("-" * 40)

def test_smtp_configuration(config_id=None):
    """Testa uma configuração SMTP específica"""
    if config_id:
        try:
            config = SMTPConfiguration.objects.get(id=config_id)
        except SMTPConfiguration.DoesNotExist:
            print(f"Configuração SMTP com ID {config_id} não encontrada")
            return False
    else:
        config = SMTPConfiguration.objects.filter(is_default=True, is_active=True).first()
    
    if not config:
        print("Nenhuma configuração SMTP encontrada")
        return False
    
    print_header(f"TESTANDO CONFIGURAÇÃO SMTP: {config.name}")
    print(f"Host: {config.host}:{config.port}")
    print(f"Username: {config.username}")
    
    try:
        # Testar com o serviço normal
        email_service = EmailService(config)
        result = email_service.send_email(
            to_email='teste@example.com',
            subject='Teste de Email',
            html_content='<h1>Teste</h1><p>Este é um email de teste.</p>',
            text_content='Teste - Este é um email de teste.'
        )
        print(f"Serviço normal: {'Sucesso' if result else 'Falha'}")
        
        # Testar com o serviço corrigido
        email_service_fixed = FixedEmailService(config)
        result_fixed = email_service_fixed.send_email(
            to_email='teste@example.com',
            subject='Teste de Email',
            html_content='<h1>Teste</h1><p>Este é um email de teste.</p>',
            text_content='Teste - Este é um email de teste.'
        )
        print(f"Serviço corrigido: {'Sucesso' if result_fixed else 'Falha'}")
        
        return result or result_fixed
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        return False

def create_email_report():
    """Cria um relatório dos emails afetados"""
    print_header("RELATÓRIO DE EMAILS AFETADOS")
    
    # Emails falhados recentes
    failed_recent = EmailQueue.objects.filter(
        status='failed',
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-created_at')
    
    print(f"Emails falhados nos últimos 7 dias: {failed_recent.count()}")
    
    # Emails pendentes
    pending = EmailQueue.objects.filter(status='pending')
    print(f"Emails pendentes: {pending.count()}")
    
    # Salvar relatório em arquivo
    report_file = f"email_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"RELATÓRIO DE EMAILS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        f.write("EMAILS FALHADOS (últimos 7 dias):\n")
        f.write("-" * 40 + "\n")
        for email in failed_recent[:50]:  # Limitar a 50 para não ficar muito grande
            f.write(f"ID: {email.id}\n")
            f.write(f"Para: {email.to_email}\n")
            f.write(f"Assunto: {email.subject}\n")
            f.write(f"Erro: {email.error_message}\n")
            f.write(f"Data: {email.created_at}\n")
            f.write("-" * 20 + "\n")
        
        f.write(f"\nEMAILS PENDENTES:\n")
        f.write("-" * 40 + "\n")
        for email in pending:
            f.write(f"ID: {email.id}\n")
            f.write(f"Para: {email.to_email}\n")
            f.write(f"Assunto: {email.subject}\n")
            f.write(f"Agendado: {email.scheduled_at}\n")
            f.write("-" * 20 + "\n")
    
    print(f"Relatório salvo em: {report_file}")

def suggest_solutions():
    """Sugere soluções para o problema"""
    print_header("SOLUÇÕES SUGERIDAS")
    
    print("1. PROBLEMA IDENTIFICADO:")
    print("   - O IP do servidor está sendo bloqueado pelo servidor SMTP")
    print("   - Erro: 'IP bloqueado por envio de phishing e malware'")
    print()
    
    print("2. SOLUÇÕES IMEDIATAS:")
    print("   a) Contatar o administrador do servidor SMTP para desbloquear o IP")
    print("   b) Usar uma configuração SMTP alternativa (Gmail, etc.)")
    print("   c) Configurar um novo servidor SMTP")
    print()
    
    print("3. AÇÕES RECOMENDADAS:")
    print("   a) Atualizar a senha na configuração SMTP atual")
    print("   b) Testar a conectividade com o servidor SMTP")
    print("   c) Verificar se o IP foi desbloqueado")
    print("   d) Considerar usar um serviço de email terceirizado")
    print()
    
    print("4. COMANDOS PARA EXECUTAR:")
    print("   - Para testar configuração: python3 fix_email_system.py test")
    print("   - Para gerar relatório: python3 fix_email_system.py report")
    print("   - Para verificar status: python3 fix_email_system.py status")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            if len(sys.argv) > 2:
                config_id = int(sys.argv[2])
                test_smtp_configuration(config_id)
            else:
                test_smtp_configuration()
        elif command == "report":
            create_email_report()
        elif command == "status":
            check_email_status()
        elif command == "configs":
            check_smtp_configurations()
        else:
            print("Comando não reconhecido. Use: test, report, status, ou configs")
    else:
        print_header("DIAGNÓSTICO DO SISTEMA DE EMAIL")
        
        check_smtp_configurations()
        check_email_status()
        
        print_header("TESTE DA CONFIGURAÇÃO PADRÃO")
        test_smtp_configuration()
        
        create_email_report()
        suggest_solutions()

if __name__ == "__main__":
    main()
