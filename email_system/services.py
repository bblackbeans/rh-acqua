"""
Serviços para o sistema de email
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
import logging
from typing import Dict, Any, Optional
from .models import SMTPConfiguration, EmailTemplate, EmailTrigger, EmailQueue, EmailLog

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço principal para envio de emails
    """
    
    def __init__(self, smtp_config: Optional[SMTPConfiguration] = None):
        self.smtp_config = smtp_config or self._get_default_smtp_config()
    
    def _get_default_smtp_config(self) -> Optional[SMTPConfiguration]:
        """Obtém a configuração SMTP padrão"""
        try:
            return SMTPConfiguration.objects.filter(is_default=True, is_active=True).first()
        except Exception as e:
            logger.error(f"Erro ao obter configuração SMTP padrão: {e}")
            return None
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        to_name: str = None,
        from_email: str = None,
        from_name: str = None
    ) -> bool:
        """
        Envia um email usando a configuração SMTP
        """
        if not self.smtp_config:
            logger.error("Nenhuma configuração SMTP disponível")
            return False
        
        try:
            # Preparar dados do remetente
            sender_email = from_email or self.smtp_config.from_email
            sender_name = from_name or self.smtp_config.from_name
            
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{sender_name} <{sender_email}>"
            message["To"] = to_email
            
            # Adicionar conteúdo
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Conectar e enviar
            context = ssl.create_default_context()
            
            if self.smtp_config.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_config.host, self.smtp_config.port, context=context)
            else:
                server = smtplib.SMTP(self.smtp_config.host, self.smtp_config.port)
                if self.smtp_config.use_tls:
                    server.starttls(context=context)
            
            server.login(self.smtp_config.username, self.smtp_config.password)
            server.send_message(message)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {e}")
            return False


class EmailTemplateService:
    """
    Serviço para renderização de templates de email
    """
    
    @staticmethod
    def render_template(template: EmailTemplate, context_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Renderiza um template de email com os dados fornecidos
        """
        try:
            # Renderizar assunto
            subject_template = Template(template.subject)
            subject_context = Context(context_data)
            rendered_subject = subject_template.render(subject_context)
            
            # Renderizar conteúdo HTML
            html_template = Template(template.html_content)
            html_context = Context(context_data)
            rendered_html = html_template.render(html_context)
            
            # Renderizar conteúdo texto (se existir)
            rendered_text = None
            if template.text_content:
                text_template = Template(template.text_content)
                text_context = Context(context_data)
                rendered_text = text_template.render(text_context)
            
            return {
                'subject': rendered_subject,
                'html_content': rendered_html,
                'text_content': rendered_text
            }
            
        except Exception as e:
            logger.error(f"Erro ao renderizar template {template.name}: {e}")
            raise


class EmailQueueService:
    """
    Serviço para gerenciamento da fila de emails
    """
    
    @staticmethod
    def add_to_queue(
        trigger: EmailTrigger,
        to_email: str,
        context_data: Dict[str, Any],
        to_name: str = None,
        priority: int = None,
        delay_minutes: int = None
    ) -> EmailQueue:
        """
        Adiciona um email à fila para processamento
        """
        try:
            # Renderizar template
            rendered_content = EmailTemplateService.render_template(trigger.template, context_data)
            
            # Calcular data de agendamento
            scheduled_at = timezone.now()
            if delay_minutes is not None:
                scheduled_at = scheduled_at + timezone.timedelta(minutes=delay_minutes)
            elif trigger.delay_minutes > 0:
                scheduled_at = scheduled_at + timezone.timedelta(minutes=trigger.delay_minutes)
            
            # Criar item na fila
            email_queue = EmailQueue.objects.create(
                trigger=trigger,
                to_email=to_email,
                to_name=to_name,
                subject=rendered_content['subject'],
                html_content=rendered_content['html_content'],
                text_content=rendered_content['text_content'],
                context_data=context_data,
                priority=priority or trigger.priority,
                scheduled_at=scheduled_at
            )
            
            logger.info(f"Email adicionado à fila: {email_queue.id}")
            return email_queue
            
        except Exception as e:
            logger.error(f"Erro ao adicionar email à fila: {e}")
            raise
    
    @staticmethod
    def process_queue_item(email_queue: EmailQueue) -> bool:
        """
        Processa um item da fila de emails
        """
        start_time = timezone.now()
        
        try:
            # Marcar como processando
            email_queue.status = 'processing'
            email_queue.save()
            
            # Obter configuração SMTP
            smtp_config = email_queue.trigger.smtp_config
            from .email_service_fix import FixedEmailService
            email_service = FixedEmailService(smtp_config)
            
            # Enviar email
            success = email_service.send_email(
                to_email=email_queue.to_email,
                subject=email_queue.subject,
                html_content=email_queue.html_content,
                text_content=email_queue.text_content,
                to_name=email_queue.to_name
            )
            
            # Atualizar status
            if success:
                email_queue.status = 'sent'
                email_queue.sent_at = timezone.now()
                email_queue.error_message = None
            else:
                email_queue.status = 'failed'
                email_queue.error_message = "Falha no envio do email"
            
            email_queue.retry_count += 1
            email_queue.save()
            
            # Calcular tempo de processamento
            processing_time = (timezone.now() - start_time).total_seconds()
            
            # Criar log
            EmailLog.objects.create(
                email_queue=email_queue,
                trigger=email_queue.trigger,
                smtp_config=smtp_config,
                to_email=email_queue.to_email,
                to_name=email_queue.to_name,
                subject=email_queue.subject,
                status=email_queue.status,
                sent_at=email_queue.sent_at,
                error_message=email_queue.error_message,
                retry_count=email_queue.retry_count,
                processing_time=processing_time
            )
            
            logger.info(f"Email processado: {email_queue.id} - Status: {email_queue.status}")
            return success
            
        except Exception as e:
            # Marcar como falhou
            email_queue.status = 'failed'
            email_queue.error_message = str(e)
            email_queue.retry_count += 1
            email_queue.save()
            
            # Calcular tempo de processamento
            processing_time = (timezone.now() - start_time).total_seconds()
            
            # Criar log
            EmailLog.objects.create(
                email_queue=email_queue,
                trigger=email_queue.trigger,
                smtp_config=email_queue.trigger.smtp_config,
                to_email=email_queue.to_email,
                to_name=email_queue.to_name,
                subject=email_queue.subject,
                status='failed',
                error_message=str(e),
                retry_count=email_queue.retry_count,
                processing_time=processing_time
            )
            
            logger.error(f"Erro ao processar email {email_queue.id}: {e}")
            return False
    
    @staticmethod
    def get_pending_emails(limit: int = 10) -> list:
        """
        Obtém emails pendentes para processamento
        """
        return EmailQueue.objects.filter(
            status='pending',
            scheduled_at__lte=timezone.now()
        ).order_by('-priority', 'scheduled_at')[:limit]
    
    @staticmethod
    def retry_failed_emails(limit: int = 5) -> int:
        """
        Tenta reenviar emails que falharam
        """
        from django.db import models
        failed_emails = EmailQueue.objects.filter(
            status='failed'
        ).filter(
            models.Q(retry_count__lt=models.F('max_retries'))
        ).order_by('-priority', 'scheduled_at')[:limit]
        
        retried_count = 0
        for email_queue in failed_emails:
            if email_queue.can_retry():
                email_queue.status = 'pending'
                email_queue.scheduled_at = timezone.now()
                email_queue.save()
                retried_count += 1
        
        return retried_count


class EmailTriggerService:
    """
    Serviço para gerenciamento de gatilhos de email
    """
    
    @staticmethod
    def trigger_email(
        trigger_type: str,
        to_email: str,
        context_data: Dict[str, Any],
        to_name: str = None,
        priority: int = None,
        delay_minutes: int = None
    ) -> Optional[EmailQueue]:
        """
        Dispara um email baseado no tipo de gatilho
        """
        try:
            # Buscar gatilhos ativos para este tipo
            triggers = EmailTrigger.objects.filter(
                trigger_type=trigger_type,
                is_active=True
            ).order_by('-priority')
            
            if not triggers.exists():
                logger.warning(f"Nenhum gatilho ativo encontrado para: {trigger_type}")
                return None
            
            # Usar o primeiro gatilho (maior prioridade)
            trigger = triggers.first()
            
            # Verificar condições (se existirem)
            if trigger.conditions:
                if not EmailTriggerService._check_conditions(trigger.conditions, context_data):
                    logger.info(f"Condições não atendidas para gatilho: {trigger.name}")
                    return None
            
            # Adicionar à fila
            return EmailQueueService.add_to_queue(
                trigger=trigger,
                to_email=to_email,
                context_data=context_data,
                to_name=to_name,
                priority=priority,
                delay_minutes=delay_minutes
            )
            
        except Exception as e:
            logger.error(f"Erro ao disparar email {trigger_type}: {e}")
            return None
    
    @staticmethod
    def _check_conditions(conditions: Dict[str, Any], context_data: Dict[str, Any]) -> bool:
        """
        Verifica se as condições do gatilho são atendidas
        """
        try:
            for key, expected_value in conditions.items():
                if key not in context_data:
                    return False
                
                actual_value = context_data[key]
                if actual_value != expected_value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar condições: {e}")
            return False
