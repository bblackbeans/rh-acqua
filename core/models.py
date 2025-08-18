from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import UserProfile


class BaseModel(models.Model):
    """
    Modelo base com campos comuns para todos os modelos do sistema.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('Criado por')
    )
    updated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('Atualizado por')
    )
    
    class Meta:
        abstract = True


class Tag(models.Model):
    """
    Modelo para tags genéricas que podem ser associadas a diferentes entidades.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('Slug')
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_('Cor')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Modelo para categorias genéricas que podem ser associadas a diferentes entidades.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('Slug')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Categoria Pai')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Ícone')
    )
    
    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class Attachment(models.Model):
    """
    Modelo para anexos que podem ser associados a diferentes entidades.
    """
    file = models.FileField(
        upload_to='attachments/%Y/%m/',
        verbose_name=_('Arquivo')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    content_type = models.CharField(
        max_length=100,
        verbose_name=_('Tipo de Conteúdo')
    )
    size = models.PositiveIntegerField(
        verbose_name=_('Tamanho (bytes)')
    )
    uploaded_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments',
        verbose_name=_('Enviado por')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Envio')
    )
    
    class Meta:
        verbose_name = _('Anexo')
        verbose_name_plural = _('Anexos')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name


class Comment(BaseModel):
    """
    Modelo para comentários que podem ser associados a diferentes entidades.
    """
    content = models.TextField(
        verbose_name=_('Conteúdo')
    )
    content_type = models.CharField(
        max_length=100,
        verbose_name=_('Tipo de Conteúdo')
    )
    object_id = models.CharField(
        max_length=100,
        verbose_name=_('ID do Objeto')
    )
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Autor')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Comentário Pai')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    
    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comentário de {self.author} em {self.created_at}"


class Dashboard(BaseModel):
    """
    Modelo para dashboards personalizados.
    """
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição')
    )
    layout = models.JSONField(
        default=dict,
        verbose_name=_('Layout')
    )
    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='core_dashboards',
        verbose_name=_('Proprietário')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Padrão')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Público')
    )
    
    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboards')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Widget(BaseModel):
    """
    Modelo para widgets que podem ser adicionados a dashboards.
    """
    WIDGET_TYPES = (
        ('chart', _('Gráfico')),
        ('table', _('Tabela')),
        ('metric', _('Métrica')),
        ('list', _('Lista')),
        ('custom', _('Personalizado')),
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES,
        verbose_name=_('Tipo de Widget')
    )
    data_source = models.CharField(
        max_length=255,
        verbose_name=_('Fonte de Dados')
    )
    configuration = models.JSONField(
        default=dict,
        verbose_name=_('Configuração')
    )
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_('Dashboard')
    )
    position_x = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Posição X')
    )
    position_y = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Posição Y')
    )
    width = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Largura')
    )
    height = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Altura')
    )
    
    class Meta:
        verbose_name = _('Widget')
        verbose_name_plural = _('Widgets')
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"


class MenuItem(models.Model):
    """
    Modelo para itens de menu do sistema.
    """
    title = models.CharField(
        max_length=100,
        verbose_name=_('Título')
    )
    url = models.CharField(
        max_length=255,
        verbose_name=_('URL')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Ícone')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Item Pai')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ordem')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    required_permissions = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('Permissões Necessárias')
    )
    required_roles = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('Perfis Necessários')
    )
    
    class Meta:
        verbose_name = _('Item de Menu')
        verbose_name_plural = _('Itens de Menu')
        ordering = ['parent__order', 'parent__id', 'order']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.title}"
        return self.title


class FAQ(BaseModel):
    """
    Modelo para perguntas frequentes.
    """
    question = models.CharField(
        max_length=255,
        verbose_name=_('Pergunta')
    )
    answer = models.TextField(
        verbose_name=_('Resposta')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faqs',
        verbose_name=_('Categoria')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='faqs',
        verbose_name=_('Tags')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ordem')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    
    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question


class Feedback(BaseModel):
    """
    Modelo para feedback dos usuários sobre o sistema.
    """
    FEEDBACK_TYPES = (
        ('bug', _('Bug')),
        ('feature', _('Sugestão de Funcionalidade')),
        ('improvement', _('Melhoria')),
        ('other', _('Outro')),
    )
    
    PRIORITY_LEVELS = (
        ('low', _('Baixa')),
        ('medium', _('Média')),
        ('high', _('Alta')),
        ('critical', _('Crítica')),
    )
    
    STATUS_CHOICES = (
        ('new', _('Novo')),
        ('in_progress', _('Em Andamento')),
        ('resolved', _('Resolvido')),
        ('closed', _('Fechado')),
        ('rejected', _('Rejeitado')),
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    description = models.TextField(
        verbose_name=_('Descrição')
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        verbose_name=_('Tipo de Feedback')
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name=_('Prioridade')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name=_('Status')
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name=_('Usuário')
    )
    assigned_to = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feedback',
        verbose_name=_('Atribuído a')
    )
    resolution = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Resolução')
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolvido em')
    )
    
    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedbacks')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def resolve(self, resolution, resolved_by):
        """
        Marca o feedback como resolvido.
        """
        self.status = 'resolved'
        self.resolution = resolution
        self.resolved_at = timezone.now()
        self.updated_by = resolved_by
        self.save(update_fields=['status', 'resolution', 'resolved_at', 'updated_by', 'updated_at'])


class Announcement(BaseModel):
    """
    Modelo para anúncios e comunicados do sistema.
    """
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo')
    )
    start_date = models.DateTimeField(
        verbose_name=_('Data de Início')
    )
    end_date = models.DateTimeField(
        verbose_name=_('Data de Término')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    target_roles = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('Perfis Alvo')
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name=_('Importante')
    )
    
    class Meta:
        verbose_name = _('Anúncio')
        verbose_name_plural = _('Anúncios')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_current(self):
        """
        Verifica se o anúncio está dentro do período de exibição.
        """
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active
