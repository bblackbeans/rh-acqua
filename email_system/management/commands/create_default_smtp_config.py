"""
Comando para criar configuração SMTP padrão
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from email_system.models import SMTPConfiguration, EmailTrigger, EmailTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria configuração SMTP padrão e gatilhos básicos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='smtp.gmail.com',
            help='Servidor SMTP (padrão: smtp.gmail.com)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=587,
            help='Porta SMTP (padrão: 587)'
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Usuário SMTP'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Senha SMTP'
        )
        parser.add_argument(
            '--from-email',
            type=str,
            required=True,
            help='Email remetente'
        )
        parser.add_argument(
            '--from-name',
            type=str,
            default='RH Acqua',
            help='Nome do remetente (padrão: RH Acqua)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Criando configuração SMTP padrão...')
        
        # Obter ou criar usuário admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('Nenhum usuário admin encontrado. Usando None para created_by.')
            )
            admin_user = None
        
        # Criar configuração SMTP
        smtp_config, created = SMTPConfiguration.objects.get_or_create(
            name='Configuração Padrão',
            defaults={
                'host': options['host'],
                'port': options['port'],
                'use_tls': True,
                'use_ssl': False,
                'username': options['username'],
                'password': options['password'],
                'from_email': options['from_email'],
                'from_name': options['from_name'],
                'is_active': True,
                'is_default': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Configuração SMTP criada: {smtp_config.name}')
        else:
            self.stdout.write(f'• Configuração SMTP já existe: {smtp_config.name}')
        
        # Criar gatilhos básicos
        self.create_basic_triggers(smtp_config, admin_user)
        
        self.stdout.write(
            self.style.SUCCESS('Configuração SMTP e gatilhos criados com sucesso!')
        )

    def create_basic_triggers(self, smtp_config, admin_user):
        """Cria gatilhos básicos para os templates existentes"""
        
        # Gatilho para cadastro de usuário
        template = EmailTemplate.objects.filter(trigger_type='user_registration').first()
        if template:
            trigger, created = EmailTrigger.objects.get_or_create(
                name='Cadastro de Usuário',
                trigger_type='user_registration',
                defaults={
                    'template': template,
                    'smtp_config': smtp_config,
                    'is_active': True,
                    'priority': 2,
                    'delay_minutes': 0,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'✓ Gatilho "Cadastro de Usuário" criado')
            else:
                self.stdout.write(f'• Gatilho "Cadastro de Usuário" já existe')
        
        # Gatilho para candidatura realizada
        template = EmailTemplate.objects.filter(trigger_type='application_submitted').first()
        if template:
            trigger, created = EmailTrigger.objects.get_or_create(
                name='Candidatura Realizada',
                trigger_type='application_submitted',
                defaults={
                    'template': template,
                    'smtp_config': smtp_config,
                    'is_active': True,
                    'priority': 2,
                    'delay_minutes': 0,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'✓ Gatilho "Candidatura Realizada" criado')
            else:
                self.stdout.write(f'• Gatilho "Candidatura Realizada" já existe')
        
        # Gatilho para candidatura aprovada
        template = EmailTemplate.objects.filter(trigger_type='application_approved').first()
        if template:
            trigger, created = EmailTrigger.objects.get_or_create(
                name='Candidatura Aprovada',
                trigger_type='application_approved',
                defaults={
                    'template': template,
                    'smtp_config': smtp_config,
                    'is_active': True,
                    'priority': 3,
                    'delay_minutes': 0,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'✓ Gatilho "Candidatura Aprovada" criado')
            else:
                self.stdout.write(f'• Gatilho "Candidatura Aprovada" já existe')
        
        # Gatilho para candidatura rejeitada
        template = EmailTemplate.objects.filter(trigger_type='application_rejected').first()
        if template:
            trigger, created = EmailTrigger.objects.get_or_create(
                name='Candidatura Rejeitada',
                trigger_type='application_rejected',
                defaults={
                    'template': template,
                    'smtp_config': smtp_config,
                    'is_active': True,
                    'priority': 2,
                    'delay_minutes': 0,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'✓ Gatilho "Candidatura Rejeitada" criado')
            else:
                self.stdout.write(f'• Gatilho "Candidatura Rejeitada" já existe')
        
        # Gatilho para entrevista agendada
        template = EmailTemplate.objects.filter(trigger_type='interview_scheduled').first()
        if template:
            trigger, created = EmailTrigger.objects.get_or_create(
                name='Entrevista Agendada',
                trigger_type='interview_scheduled',
                defaults={
                    'template': template,
                    'smtp_config': smtp_config,
                    'is_active': True,
                    'priority': 3,
                    'delay_minutes': 0,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'✓ Gatilho "Entrevista Agendada" criado')
            else:
                self.stdout.write(f'• Gatilho "Entrevista Agendada" já existe')
