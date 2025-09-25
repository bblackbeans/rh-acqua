#!/usr/bin/env python3
"""
Script para tentar usar uma configuração SMTP alternativa
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/institutoacquaor/public_html/rh-acqua')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from email_system.models import EmailQueue, SMTPConfiguration, EmailTrigger
from email_system.email_service_fix import FixedEmailService
from django.utils import timezone

def create_gmail_config():
    """Cria uma configuração SMTP do Gmail se não existir"""
    print("=== CRIANDO CONFIGURAÇÃO GMAIL ===")
    
    # Verificar se já existe uma configuração Gmail ativa
    gmail_config = SMTPConfiguration.objects.filter(
        name__icontains='gmail',
        is_active=True
    ).first()
    
    if gmail_config:
        print(f"Configuração Gmail já existe: {gmail_config.name}")
        return gmail_config
    
    # Criar nova configuração Gmail
    gmail_config = SMTPConfiguration.objects.create(
        name='Gmail SMTP Alternativo',
        host='smtp.gmail.com',
        port=587,
        use_tls=True,
        use_ssl=False,
        username='seu-email@gmail.com',  # Você precisa alterar isso
        password='sua-senha-de-app',     # Você precisa alterar isso
        from_email='seu-email@gmail.com', # Você precisa alterar isso
        from_name='RH Acqua',
        is_active=True,
        is_default=False
    )
    
    print(f"Configuração Gmail criada com ID: {gmail_config.id}")
    print("IMPORTANTE: Você precisa atualizar:")
    print("1. Username: seu-email@gmail.com")
    print("2. Password: sua senha de aplicativo do Gmail")
    print("3. From Email: seu-email@gmail.com")
    
    return gmail_config

def test_gmail_connection():
    """Testa conexão com Gmail"""
    print("\n=== TESTANDO CONEXÃO GMAIL ===")
    
    gmail_config = SMTPConfiguration.objects.filter(
        name__icontains='gmail',
        is_active=True
    ).first()
    
    if not gmail_config:
        print("Nenhuma configuração Gmail encontrada")
        return False
    
    if gmail_config.username == 'seu-email@gmail.com':
        print("ATENÇÃO: Configure primeiro o email e senha do Gmail!")
        print("1. Acesse o Django Admin")
        print("2. Vá para Email System > Configurações SMTP")
        print("3. Edite a configuração Gmail")
        print("4. Atualize username, password e from_email")
        return False
    
    try:
        email_service = FixedEmailService(gmail_config)
        result = email_service.send_email(
            to_email='teste@example.com',
            subject='Teste Gmail',
            html_content='<h1>Teste Gmail</h1><p>Este é um teste.</p>',
            text_content='Teste Gmail - Este é um teste.'
        )
        
        if result:
            print("✅ Conexão Gmail funcionando!")
            return True
        else:
            print("❌ Falha na conexão Gmail")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão Gmail: {e}")
        return False

def switch_to_gmail_config():
    """Muda a configuração padrão para Gmail"""
    print("\n=== MUDANDO PARA CONFIGURAÇÃO GMAIL ===")
    
    # Desativar configuração atual
    current_default = SMTPConfiguration.objects.filter(is_default=True).first()
    if current_default:
        current_default.is_default = False
        current_default.save()
        print(f"Configuração padrão anterior desativada: {current_default.name}")
    
    # Ativar configuração Gmail
    gmail_config = SMTPConfiguration.objects.filter(
        name__icontains='gmail',
        is_active=True
    ).first()
    
    if gmail_config:
        gmail_config.is_default = True
        gmail_config.save()
        print(f"Nova configuração padrão: {gmail_config.name}")
        return True
    else:
        print("Nenhuma configuração Gmail encontrada")
        return False

def retry_failed_emails_with_gmail():
    """Tenta reenviar emails falhados usando Gmail"""
    print("\n=== TENTANDO REENVIAR EMAILS COM GMAIL ===")
    
    # Verificar se Gmail está configurado
    gmail_config = SMTPConfiguration.objects.filter(
        name__icontains='gmail',
        is_active=True,
        is_default=True
    ).first()
    
    if not gmail_config:
        print("Gmail não está configurado como padrão")
        return
    
    if gmail_config.username == 'seu-email@gmail.com':
        print("Gmail não está configurado corretamente")
        return
    
    # Pegar alguns emails falhados para tentar reenviar
    failed_emails = EmailQueue.objects.filter(
        status='failed',
        retry_count__lt=3
    )[:10]  # Limitar a 10 para teste
    
    print(f"Tentando reenviar {failed_emails.count()} emails...")
    
    success_count = 0
    for email in failed_emails:
        try:
            # Marcar como processando
            email.status = 'processing'
            email.save()
            
            # Tentar enviar com Gmail
            email_service = FixedEmailService(gmail_config)
            result = email_service.send_email(
                to_email=email.to_email,
                subject=email.subject,
                html_content=email.html_content,
                text_content=email.text_content,
                to_name=email.to_name
            )
            
            if result:
                email.status = 'sent'
                email.sent_at = timezone.now()
                email.error_message = None
                success_count += 1
                print(f"✅ Email {email.id} enviado com sucesso")
            else:
                email.status = 'failed'
                email.error_message = "Falha no envio com Gmail"
                print(f"❌ Falha no email {email.id}")
            
            email.retry_count += 1
            email.save()
            
        except Exception as e:
            email.status = 'failed'
            email.error_message = str(e)
            email.retry_count += 1
            email.save()
            print(f"❌ Erro no email {email.id}: {e}")
    
    print(f"\nResultado: {success_count}/{failed_emails.count()} emails enviados com sucesso")

def main():
    print("=== SCRIPT DE CORREÇÃO DE EMAIL COM GMAIL ===")
    
    # 1. Criar configuração Gmail
    create_gmail_config()
    
    # 2. Testar conexão
    if test_gmail_connection():
        # 3. Mudar para Gmail como padrão
        if switch_to_gmail_config():
            # 4. Tentar reenviar emails
            retry_failed_emails_with_gmail()
        else:
            print("Não foi possível mudar para configuração Gmail")
    else:
        print("\nPara configurar o Gmail:")
        print("1. Acesse o Django Admin")
        print("2. Vá para Email System > Configurações SMTP")
        print("3. Encontre a configuração Gmail")
        print("4. Atualize:")
        print("   - Username: seu email do Gmail")
        print("   - Password: senha de aplicativo do Gmail")
        print("   - From Email: seu email do Gmail")
        print("5. Execute este script novamente")

if __name__ == "__main__":
    main()


