from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationCategory(models.Model):
    """
    Categoria de notificação.
    """
    name = models.CharField(_('Nome'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    description = models.TextField(_('Descrição'), blank=True)
    icon = models.CharField(_('Ícone'), max_length=50, blank=True)
    color = models.CharField(_('Cor'), max_length=20, blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    
    class Meta:
        verbose_name = _('Categoria de Notificação')
        verbose_name_plural = _('Categorias de Notificação')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NotificationType(models.Model):
    """
    Tipo de notificação.
    """
    name = models.CharField(_('Nome'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    description = models.TextField(_('Descrição'), blank=True)
    category = models.ForeignKey(
        NotificationCategory,
        on_delete=models.CASCADE,
        related_name='notification_types',
        verbose_name=_('Categoria')
    )
    icon = models.CharField(_('Ícone'), max_length=50, blank=True)
    color = models.CharField(_('Cor'), max_length=20, blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    
    # Canais disponíveis para este tipo de notificação
    email_available = models.BooleanField(_('Disponível por E-mail'), default=True)
    push_available = models.BooleanField(_('Disponível por Push'), default=True)
    sms_available = models.BooleanField(_('Disponível por SMS'), default=False)
    
    # Templates para mensagens
    email_subject_template = models.CharField(_('Template de Assunto de E-mail'), max_length=255, blank=True)
    email_body_template = models.TextField(_('Template de Corpo de E-mail'), blank=True)
    push_title_template = models.CharField(_('Template de Título de Push'), max_length=255, blank=True)
    push_body_template = models.TextField(_('Template de Corpo de Push'), blank=True)
    sms_template = models.TextField(_('Template de SMS'), blank=True)
    
    class Meta:
        verbose_name = _('Tipo de Notificação')
        verbose_name_plural = _('Tipos de Notificação')
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """
    Preferência de notificação por usuário.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('Usuário')
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name=_('Tipo de Notificação')
    )
    
    # Canais habilitados para este usuário
    email_enabled = models.BooleanField(_('E-mail Habilitado'), default=True)
    push_enabled = models.BooleanField(_('Push Habilitado'), default=True)
    sms_enabled = models.BooleanField(_('SMS Habilitado'), default=False)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Preferência de Notificação')
        verbose_name_plural = _('Preferências de Notificação')
        unique_together = ('user', 'notification_type')
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type.name}"


class Notification(models.Model):
    """
    Notificação para um usuário.
    """
    STATUS_CHOICES = (
        ('unread', _('Não Lida')),
        ('read', _('Lida')),
        ('archived', _('Arquivada')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Baixa')),
        ('normal', _('Normal')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Usuário')
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Tipo de Notificação')
    )
    title = models.CharField(_('Título'), max_length=255)
    message = models.TextField(_('Mensagem'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='unread')
    priority = models.CharField(_('Prioridade'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Link para a notificação
    url = models.CharField(_('URL'), max_length=255, blank=True)
    
    # Objeto relacionado (opcional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('Tipo de Conteúdo')
    )
    object_id = models.PositiveIntegerField(_('ID do Objeto'), blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(_('Metadados'), blank=True, null=True)
    
    # Datas
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    read_at = models.DateTimeField(_('Lido em'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Notificação')
        verbose_name_plural = _('Notificações')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def mark_as_read(self):
        """
        Marca a notificação como lida.
        """
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def mark_as_unread(self):
        """
        Marca a notificação como não lida.
        """
        if self.status != 'unread':
            self.status = 'unread'
            self.read_at = None
            self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def archive(self):
        """
        Arquiva a notificação.
        """
        if self.status != 'archived':
            self.status = 'archived'
            self.save(update_fields=['status', 'updated_at'])
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta da notificação.
        """
        if self.url:
            return self.url
        
        return reverse('notifications:notification_detail', kwargs={'pk': self.pk})


class NotificationDelivery(models.Model):
    """
    Registro de entrega de notificação.
    """
    CHANNEL_CHOICES = (
        ('email', _('E-mail')),
        ('push', _('Push')),
        ('sms', _('SMS')),
        ('in_app', _('No Aplicativo')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('sent', _('Enviado')),
        ('delivered', _('Entregue')),
        ('failed', _('Falhou')),
    )
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_('Notificação')
    )
    channel = models.CharField(_('Canal'), max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Detalhes da entrega
    sent_at = models.DateTimeField(_('Enviado em'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('Entregue em'), blank=True, null=True)
    error_message = models.TextField(_('Mensagem de Erro'), blank=True)
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(_('Metadados'), blank=True, null=True)
    
    # Datas
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Entrega de Notificação')
        verbose_name_plural = _('Entregas de Notificação')
        ordering = ['-created_at']
        unique_together = ('notification', 'channel')
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_channel_display()}"
    
    def mark_as_sent(self):
        """
        Marca a entrega como enviada.
        """
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_as_delivered(self):
        """
        Marca a entrega como entregue.
        """
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def mark_as_failed(self, error_message=''):
        """
        Marca a entrega como falha.
        """
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])


class Message(models.Model):
    """
    Mensagem entre usuários.
    """
    STATUS_CHOICES = (
        ('unread', _('Não Lida')),
        ('read', _('Lida')),
        ('archived', _('Arquivada')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Baixa')),
        ('normal', _('Normal')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Remetente')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('Destinatário')
    )
    subject = models.CharField(_('Assunto'), max_length=255)
    body = models.TextField(_('Corpo'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='unread')
    priority = models.CharField(_('Prioridade'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Mensagem pai (para respostas)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies',
        verbose_name=_('Mensagem Pai')
    )
    
    # Objeto relacionado (opcional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('Tipo de Conteúdo')
    )
    object_id = models.PositiveIntegerField(_('ID do Objeto'), blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(_('Metadados'), blank=True, null=True)
    
    # Datas
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    read_at = models.DateTimeField(_('Lido em'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Mensagem')
        verbose_name_plural = _('Mensagens')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.subject
    
    def mark_as_read(self):
        """
        Marca a mensagem como lida.
        """
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def mark_as_unread(self):
        """
        Marca a mensagem como não lida.
        """
        if self.status != 'unread':
            self.status = 'unread'
            self.read_at = None
            self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def archive(self):
        """
        Arquiva a mensagem.
        """
        if self.status != 'archived':
            self.status = 'archived'
            self.save(update_fields=['status', 'updated_at'])
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta da mensagem.
        """
        return reverse('notifications:message_detail', kwargs={'pk': self.pk})


class Announcement(models.Model):
    """
    Anúncio para todos os usuários ou grupos específicos.
    """
    STATUS_CHOICES = (
        ('draft', _('Rascunho')),
        ('scheduled', _('Agendado')),
        ('published', _('Publicado')),
        ('expired', _('Expirado')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Baixa')),
        ('normal', _('Normal')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    )
    
    title = models.CharField(_('Título'), max_length=255)
    content = models.TextField(_('Conteúdo'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(_('Prioridade'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Datas de publicação
    publish_from = models.DateTimeField(_('Publicar a partir de'), blank=True, null=True)
    publish_until = models.DateTimeField(_('Publicar até'), blank=True, null=True)
    
    # Público-alvo
    target_all_users = models.BooleanField(_('Todos os Usuários'), default=False)
    target_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='announcements',
        verbose_name=_('Grupos Alvo')
    )
    target_roles = models.JSONField(_('Perfis Alvo'), blank=True, null=True)
    
    # Opções de exibição
    show_on_dashboard = models.BooleanField(_('Exibir no Dashboard'), default=True)
    show_as_popup = models.BooleanField(_('Exibir como Popup'), default=False)
    dismissible = models.BooleanField(_('Pode ser Dispensado'), default=True)
    
    # URL relacionada
    url = models.CharField(_('URL'), max_length=255, blank=True)
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(_('Metadados'), blank=True, null=True)
    
    # Datas
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_announcements',
        verbose_name=_('Criado por')
    )
    
    class Meta:
        verbose_name = _('Anúncio')
        verbose_name_plural = _('Anúncios')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_active(self):
        """
        Verifica se o anúncio está ativo.
        """
        now = timezone.now()
        
        if self.status != 'published':
            return False
        
        if self.publish_from and self.publish_from > now:
            return False
        
        if self.publish_until and self.publish_until < now:
            return False
        
        return True
    
    def publish(self):
        """
        Publica o anúncio.
        """
        if self.status == 'draft':
            self.status = 'published'
            self.save(update_fields=['status', 'updated_at'])
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta do anúncio.
        """
        return reverse('notifications:announcement_detail', kwargs={'pk': self.pk})


class AnnouncementDismissal(models.Model):
    """
    Registro de dispensa de anúncio por usuário.
    """
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='dismissals',
        verbose_name=_('Anúncio')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dismissed_announcements',
        verbose_name=_('Usuário')
    )
    dismissed_at = models.DateTimeField(_('Dispensado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Dispensa de Anúncio')
        verbose_name_plural = _('Dispensas de Anúncio')
        unique_together = ('announcement', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.announcement.title}"
