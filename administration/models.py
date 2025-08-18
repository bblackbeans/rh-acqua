from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import UserProfile


class Hospital(models.Model):
    """
    Modelo para unidades hospitalares.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Código')
    )
    address = models.TextField(
        verbose_name=_('Endereço')
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_('Cidade')
    )
    state = models.CharField(
        max_length=2,
        verbose_name=_('Estado')
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('CEP')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Telefone')
    )
    email = models.EmailField(
        verbose_name=_('E-mail')
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Website')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    logo = models.ImageField(
        upload_to='hospital_logos/',
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    
    class Meta:
        verbose_name = _('Hospital')
        verbose_name_plural = _('Hospitais')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Modelo para departamentos/setores.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    code = models.CharField(
        max_length=50,
        verbose_name=_('Código')
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_('Hospital')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    manager = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_('Gerente')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    
    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')
        ordering = ['hospital', 'name']
        unique_together = ('code', 'hospital')
    
    def __str__(self):
        return f"{self.name} - {self.hospital.name}"


class SystemConfiguration(models.Model):
    """
    Modelo para configurações do sistema.
    """
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Chave')
    )
    value = models.TextField(
        verbose_name=_('Valor')
    )
    value_type = models.CharField(
        max_length=20,
        choices=(
            ('string', _('Texto')),
            ('integer', _('Número Inteiro')),
            ('float', _('Número Decimal')),
            ('boolean', _('Booleano')),
            ('json', _('JSON')),
            ('date', _('Data')),
            ('datetime', _('Data e Hora')),
        ),
        default='string',
        verbose_name=_('Tipo de Valor')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    category = models.CharField(
        max_length=100,
        verbose_name=_('Categoria')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Público')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    updated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_configurations',
        verbose_name=_('Atualizado por')
    )
    
    class Meta:
        verbose_name = _('Configuração do Sistema')
        verbose_name_plural = _('Configurações do Sistema')
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} ({self.category})"
    
    def get_typed_value(self):
        """
        Retorna o valor convertido para o tipo correto.
        """
        if self.value_type == 'string':
            return self.value
        elif self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 't', 'y', 'yes', 'sim')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        elif self.value_type == 'date':
            from django.utils.dateparse import parse_date
            return parse_date(self.value)
        elif self.value_type == 'datetime':
            from django.utils.dateparse import parse_datetime
            return parse_datetime(self.value)
        return self.value


class SystemLog(models.Model):
    """
    Modelo para logs do sistema.
    """
    LOG_LEVELS = (
        ('debug', _('Debug')),
        ('info', _('Informação')),
        ('warning', _('Aviso')),
        ('error', _('Erro')),
        ('critical', _('Crítico')),
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data e Hora')
    )
    level = models.CharField(
        max_length=10,
        choices=LOG_LEVELS,
        default='info',
        verbose_name=_('Nível')
    )
    message = models.TextField(
        verbose_name=_('Mensagem')
    )
    source = models.CharField(
        max_length=255,
        verbose_name=_('Fonte')
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name=_('Usuário')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Endereço IP')
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('User Agent')
    )
    request_path = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Caminho da Requisição')
    )
    request_method = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('Método da Requisição')
    )
    additional_data = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name=_('Dados Adicionais')
    )
    
    class Meta:
        verbose_name = _('Log do Sistema')
        verbose_name_plural = _('Logs do Sistema')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} - {self.get_level_display()}: {self.message[:50]}"


class AuditLog(models.Model):
    """
    Modelo para logs de auditoria.
    """
    ACTION_TYPES = (
        ('create', _('Criação')),
        ('update', _('Atualização')),
        ('delete', _('Exclusão')),
        ('view', _('Visualização')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('other', _('Outro')),
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data e Hora')
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_('Usuário')
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_TYPES,
        verbose_name=_('Ação')
    )
    content_type = models.CharField(
        max_length=255,
        verbose_name=_('Tipo de Conteúdo')
    )
    object_id = models.CharField(
        max_length=255,
        verbose_name=_('ID do Objeto')
    )
    object_repr = models.CharField(
        max_length=255,
        verbose_name=_('Representação do Objeto')
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('Alterações')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Endereço IP')
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('User Agent')
    )
    
    class Meta:
        verbose_name = _('Log de Auditoria')
        verbose_name_plural = _('Logs de Auditoria')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.get_action_display()} - {self.object_repr}"


class Notification(models.Model):
    """
    Modelo para notificações do sistema.
    """
    NOTIFICATION_TYPES = (
        ('info', _('Informação')),
        ('success', _('Sucesso')),
        ('warning', _('Aviso')),
        ('error', _('Erro')),
    )
    
    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Destinatário')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    message = models.TextField(
        verbose_name=_('Mensagem')
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='info',
        verbose_name=_('Tipo')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data de Leitura')
    )
    url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('URL')
    )
    related_object_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Tipo de Objeto Relacionado')
    )
    related_object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('ID do Objeto Relacionado')
    )
    
    class Meta:
        verbose_name = _('Notificação')
        verbose_name_plural = _('Notificações')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient}"
    
    def mark_as_read(self):
        """
        Marca a notificação como lida.
        """
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])


class EmailTemplate(models.Model):
    """
    Modelo para templates de e-mail.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Código')
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('Assunto')
    )
    body_html = models.TextField(
        verbose_name=_('Corpo HTML')
    )
    body_text = models.TextField(
        verbose_name=_('Corpo Texto')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    variables = models.JSONField(
        default=list,
        verbose_name=_('Variáveis Disponíveis')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    updated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_email_templates',
        verbose_name=_('Atualizado por')
    )
    
    class Meta:
        verbose_name = _('Template de E-mail')
        verbose_name_plural = _('Templates de E-mail')
        ordering = ['name']
    
    def __str__(self):
        return self.name
