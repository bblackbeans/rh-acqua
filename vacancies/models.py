from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.conf import settings


class Hospital(models.Model):
    """
    Modelo para representar unidades hospitalares.
    """
    name = models.CharField(_('nome'), max_length=200)
    address = models.CharField(_('endereço'), max_length=255)
    city = models.CharField(_('cidade'), max_length=100)
    state = models.CharField(_('estado'), max_length=2)
    zip_code = models.CharField(_('CEP'), max_length=10)
    phone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    description = models.TextField(_('descrição'), blank=True, null=True)
    logo = models.ImageField(_('logo'), upload_to='hospital_logos/', blank=True, null=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('hospital')
        verbose_name_plural = _('hospitais')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Modelo para representar departamentos/setores dentro de um hospital.
    """
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments', verbose_name=_('hospital'))
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_departments', verbose_name=_('gerente'))
    is_active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('departamento')
        verbose_name_plural = _('departamentos')
        ordering = ['hospital', 'name']
        unique_together = ['hospital', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.hospital.name}"


class JobCategory(models.Model):
    """
    Modelo para categorias de vagas (ex: Enfermagem, Medicina, Administração).
    """
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    
    class Meta:
        verbose_name = _('categoria de vaga')
        verbose_name_plural = _('categorias de vagas')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Modelo para habilidades requeridas nas vagas.
    """
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='skills', verbose_name=_('categoria'))
    
    class Meta:
        verbose_name = _('habilidade')
        verbose_name_plural = _('habilidades')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Vacancy(models.Model):
    """
    Modelo para vagas de emprego.
    """
    # Status da vaga
    DRAFT = 'draft'
    PUBLISHED = 'published'
    CLOSED = 'closed'
    FILLED = 'filled'
    
    STATUS_CHOICES = (
        (DRAFT, _('Rascunho')),
        (PUBLISHED, _('Publicada')),
        (CLOSED, _('Fechada')),
        (FILLED, _('Preenchida')),
    )
    
    # Tipo de contrato
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    TEMPORARY = 'temporary'
    INTERNSHIP = 'internship'
    
    CONTRACT_TYPE_CHOICES = (
        (FULL_TIME, _('Tempo integral')),
        (PART_TIME, _('Meio período')),
        (TEMPORARY, _('Temporário')),
        (INTERNSHIP, _('Estágio')),
    )
    
    # Nível de experiência
    ENTRY = 'entry'
    JUNIOR = 'junior'
    MID = 'mid'
    SENIOR = 'senior'
    SPECIALIST = 'specialist'
    
    EXPERIENCE_LEVEL_CHOICES = (
        (ENTRY, _('Entrada')),
        (JUNIOR, _('Júnior')),
        (MID, _('Pleno')),
        (SENIOR, _('Sênior')),
        (SPECIALIST, _('Especialista')),
    )
    
    # Campos básicos
    title = models.CharField(_('título'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=250, unique=True, blank=True)
    description = models.TextField(_('descrição'), blank=True, null=True)
    requirements = models.TextField(_('requisitos'))
    benefits = models.TextField(_('benefícios'), blank=True, null=True)
    
    # Relacionamentos
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='vacancies', verbose_name=_('hospital'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='vacancies', verbose_name=_('departamento'), blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='vacancies', verbose_name=_('categoria'))
    skills = models.ManyToManyField(Skill, related_name='vacancies', verbose_name=_('habilidades'))
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_vacancies', verbose_name=_('recrutador'))
    
    # Detalhes da vaga
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    contract_type = models.CharField(_('tipo de contrato'), max_length=20, choices=CONTRACT_TYPE_CHOICES, default=FULL_TIME)
    experience_level = models.CharField(_('nível de experiência'), max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default=MID)
    salary_range_min = models.DecimalField(_('faixa salarial mínima'), max_digits=10, decimal_places=2, blank=True, null=True)
    salary_range_max = models.DecimalField(_('faixa salarial máxima'), max_digits=10, decimal_places=2, blank=True, null=True)
    is_salary_visible = models.BooleanField(_('salário visível'), default=False)
    monthly_hours = models.PositiveIntegerField(_('carga horária mensal'), blank=True, null=True, help_text=_('Carga horária mensal em horas'))
    location = models.CharField(_('localização'), max_length=200)
    is_remote = models.BooleanField(_('remoto'), default=False)
    
    # Datas
    publication_date = models.DateField(_('data de publicação'), blank=True, null=True)
    closing_date = models.DateField(_('data de encerramento'), blank=True, null=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    # Estatísticas
    views_count = models.PositiveIntegerField(_('contagem de visualizações'), default=0)
    applications_count = models.PositiveIntegerField(_('contagem de candidaturas'), default=0)
    
    class Meta:
        verbose_name = _('vaga')
        verbose_name_plural = _('vagas')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Gera um slug único baseado no título e hospital
            base_slug = slugify(f"{self.title}-{self.hospital.name}")
            slug = base_slug
            counter = 1
            
            # Verifica se o slug já existe e adiciona um número se necessário
            while Vacancy.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == self.PUBLISHED
    
    @property
    def formatted_salary_range(self):
        if self.is_salary_visible:
            if self.salary_range_min and self.salary_range_max:
                return f"R$ {self.salary_range_min} - R$ {self.salary_range_max}"
            elif self.salary_range_min:
                return f"R$ {self.salary_range_min}"
            elif self.salary_range_max:
                return f"R$ {self.salary_range_max}"
        return _("Não informado")
    
    @property
    def code(self):
        """Gera um código único para a vaga baseado no ID e ano."""
        year = self.created_at.year
        return f"VAG-{year}-{self.id:03d}"
    
    @property
    def is_new(self):
        """Verifica se a vaga foi publicada nos últimos 7 dias."""
        if not self.publication_date:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return self.publication_date >= (timezone.now().date() - timedelta(days=7))
    
    @property
    def days_since_publication(self):
        """Retorna o número de dias desde a publicação."""
        if not self.publication_date:
            return None
        from django.utils import timezone
        delta = timezone.now().date() - self.publication_date
        return delta.days


class VacancyAttachment(models.Model):
    """
    Modelo para anexos de vagas (documentos, imagens, etc).
    """
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='attachments', verbose_name=_('vaga'))
    title = models.CharField(_('título'), max_length=100)
    file = models.FileField(_('arquivo'), upload_to='vacancy_attachments/')
    description = models.TextField(_('descrição'), blank=True, null=True)
    uploaded_at = models.DateTimeField(_('enviado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('anexo de vaga')
        verbose_name_plural = _('anexos de vagas')
        ordering = ['vacancy', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.vacancy.title}"
