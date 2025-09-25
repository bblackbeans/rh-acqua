"""
Modelos para o sistema de comunicação por email
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

# Constantes para escolhas
PRIORITY_CHOICES = [
    (1, 'Baixa'),
    (2, 'Normal'),
    (3, 'Alta'),
    (4, 'Urgente'),
]

TRIGGER_CHOICES = [
    ('user_registration', 'Cadastro de Usuário'),
    ('application_submitted', 'Candidatura Realizada'),
    ('application_reviewed', 'Candidatura Analisada'),
    ('interview_scheduled', 'Entrevista Agendada'),
    ('application_approved', 'Candidatura Aprovada'),
    ('application_rejected', 'Candidatura Rejeitada'),
    ('password_reset', 'Redefinição de Senha'),
    ('welcome', 'Boas-vindas'),
    ('custom', 'Personalizado'),
]

STATUS_CHOICES = [
    ('pending', 'Pendente'),
    ('processing', 'Processando'),
    ('sent', 'Enviado'),
    ('failed', 'Falhou'),
    ('cancelled', 'Cancelado'),
]


class SMTPConfiguration(models.Model):
    """
    Configurações SMTP para envio de emails
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Configuração",
        help_text="Nome identificador para esta configuração SMTP"
    )
    host = models.CharField(
        max_length=255,
        verbose_name="Servidor SMTP",
        help_text="Endereço do servidor SMTP (ex: smtp.gmail.com)"
    )
    port = models.PositiveIntegerField(
        default=587,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name="Porta",
        help_text="Porta do servidor SMTP (587 para TLS, 465 para SSL)"
    )
    use_tls = models.BooleanField(
        default=True,
        verbose_name="Usar TLS",
        help_text="Usar TLS para conexão segura"
    )
    use_ssl = models.BooleanField(
        default=False,
        verbose_name="Usar SSL",
        help_text="Usar SSL para conexão segura"
    )
    username = models.CharField(
        max_length=255,
        verbose_name="Usuário",
        help_text="Nome de usuário para autenticação SMTP"
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Senha",
        help_text="Senha para autenticação SMTP"
    )
    from_email = models.EmailField(
        verbose_name="Email Remetente",
        help_text="Email que aparecerá como remetente"
    )
    from_name = models.CharField(
        max_length=255,
        verbose_name="Nome do Remetente",
        help_text="Nome que aparecerá como remetente"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se esta configuração está ativa"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Configuração Padrão",
        help_text="Se esta é a configuração padrão do sistema"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Configuração SMTP"
        verbose_name_plural = "Configurações SMTP"
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"

    def save(self, *args, **kwargs):
        # Garantir que apenas uma configuração seja padrão
        if self.is_default:
            SMTPConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class EmailTemplate(models.Model):
    """
    Templates de email para diferentes tipos de comunicação
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do Template",
        help_text="Nome identificador do template"
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=TRIGGER_CHOICES,
        verbose_name="Tipo de Gatilho",
        help_text="Tipo de evento que dispara este email"
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Assunto",
        help_text="Assunto do email (pode usar variáveis como {{user_name}})"
    )
    html_content = models.TextField(
        verbose_name="Conteúdo HTML",
        help_text="Conteúdo HTML do email (pode usar variáveis como {{user_name}})"
    )
    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="Conteúdo Texto",
        help_text="Conteúdo em texto simples (opcional)"
    )
    variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Variáveis Disponíveis",
        help_text="Lista de variáveis que podem ser usadas no template"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se este template está ativo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Template de Email"
        verbose_name_plural = "Templates de Email"
        ordering = ['trigger_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"


class EmailTrigger(models.Model):
    """
    Gatilhos que definem quando e como enviar emails
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do Gatilho",
        help_text="Nome identificador do gatilho"
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=TRIGGER_CHOICES,
        verbose_name="Tipo de Gatilho",
        help_text="Tipo de evento que dispara este gatilho"
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
        verbose_name="Template",
        help_text="Template de email a ser usado"
    )
    smtp_config = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.CASCADE,
        verbose_name="Configuração SMTP",
        help_text="Configuração SMTP a ser usada"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se este gatilho está ativo"
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name="Prioridade",
        help_text="Prioridade do email na fila"
    )
    delay_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Atraso (minutos)",
        help_text="Atraso em minutos antes de enviar o email"
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Condições",
        help_text="Condições adicionais para envio do email"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Gatilho de Email"
        verbose_name_plural = "Gatilhos de Email"
        ordering = ['-priority', 'trigger_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"


class EmailQueue(models.Model):
    """
    Fila de emails para processamento assíncrono
    """
    trigger = models.ForeignKey(
        EmailTrigger,
        on_delete=models.CASCADE,
        verbose_name="Gatilho",
        help_text="Gatilho que gerou este email"
    )
    to_email = models.EmailField(
        verbose_name="Email Destinatário",
        help_text="Email do destinatário"
    )
    to_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Destinatário",
        help_text="Nome do destinatário"
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Assunto",
        help_text="Assunto do email"
    )
    html_content = models.TextField(
        verbose_name="Conteúdo HTML",
        help_text="Conteúdo HTML do email"
    )
    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="Conteúdo Texto",
        help_text="Conteúdo em texto simples"
    )
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dados de Contexto",
        help_text="Dados usados para renderizar o template"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status",
        help_text="Status atual do email"
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name="Prioridade",
        help_text="Prioridade do email"
    )
    scheduled_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Agendado para",
        help_text="Data e hora agendada para envio"
    )
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Enviado em",
        help_text="Data e hora em que foi enviado"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensagem de Erro",
        help_text="Mensagem de erro em caso de falha"
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentativas",
        help_text="Número de tentativas de envio"
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        verbose_name="Máximo de Tentativas",
        help_text="Número máximo de tentativas"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Email na Fila"
        verbose_name_plural = "Fila de Emails"
        ordering = ['-priority', 'scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['priority', 'scheduled_at']),
        ]

    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.get_status_display()})"

    def can_retry(self):
        """Verifica se o email pode ser reenviado"""
        return self.retry_count < self.max_retries and self.status in ['failed', 'pending']


class EmailLog(models.Model):
    """
    Log de emails enviados para auditoria e monitoramento
    """
    email_queue = models.ForeignKey(
        EmailQueue,
        on_delete=models.CASCADE,
        verbose_name="Email da Fila",
        help_text="Email da fila que gerou este log"
    )
    trigger = models.ForeignKey(
        EmailTrigger,
        on_delete=models.CASCADE,
        verbose_name="Gatilho",
        help_text="Gatilho que gerou o email"
    )
    smtp_config = models.ForeignKey(
        SMTPConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Configuração SMTP",
        help_text="Configuração SMTP usada"
    )
    to_email = models.EmailField(
        verbose_name="Email Destinatário",
        help_text="Email do destinatário"
    )
    to_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Destinatário",
        help_text="Nome do destinatário"
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Assunto",
        help_text="Assunto do email"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Status",
        help_text="Status final do email"
    )
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Enviado em",
        help_text="Data e hora em que foi enviado"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensagem de Erro",
        help_text="Mensagem de erro em caso de falha"
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentativas",
        help_text="Número de tentativas realizadas"
    )
    processing_time = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Tempo de Processamento (s)",
        help_text="Tempo em segundos para processar o email"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Log de Email"
        verbose_name_plural = "Logs de Email"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['to_email', 'created_at']),
            models.Index(fields=['trigger', 'created_at']),
        ]

    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.get_status_display()}) - {self.created_at.strftime('%d/%m/%Y %H:%M')}"