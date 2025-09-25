"""
Serviço de email com correção para problemas de SSL
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


class FixedEmailService:
    """
    Serviço de email com correções para problemas de SSL
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
        Envia um email usando a configuração SMTP com correções SSL
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
            
            # Conectar e enviar com correções SSL
            if self.smtp_config.use_ssl:
                # Para SSL, criar contexto sem verificação de certificado
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server = smtplib.SMTP_SSL(self.smtp_config.host, self.smtp_config.port, context=context)
            else:
                server = smtplib.SMTP(self.smtp_config.host, self.smtp_config.port)
                if self.smtp_config.use_tls:
                    # Para TLS, criar contexto sem verificação de certificado
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    server.starttls(context=context)
            
            server.login(self.smtp_config.username, self.smtp_config.password)
            server.send_message(message)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {e}")
            return False
