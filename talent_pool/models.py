from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import UserProfile
from vacancies.models import Vacancy, Skill, Department


class TalentPool(models.Model):
    """
    Modelo para o banco de talentos.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
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
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='talent_pools_created',
        verbose_name=_('Criado por')
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
        verbose_name = _('Banco de Talentos')
        verbose_name_plural = _('Bancos de Talentos')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def talent_count(self):
        """Retorna o número de talentos no banco."""
        return self.talents.count()


class Talent(models.Model):
    """
    Modelo para talentos no banco de talentos.
    """
    STATUS_CHOICES = (
        ('available', _('Disponível')),
        ('considering', _('Considerando Oportunidades')),
        ('not_available', _('Indisponível')),
        ('hired', _('Contratado')),
    )
    
    SOURCE_CHOICES = (
        ('application', _('Candidatura Anterior')),
        ('referral', _('Indicação')),
        ('linkedin', _('LinkedIn')),
        ('recruitment', _('Recrutamento Ativo')),
        ('event', _('Evento')),
        ('other', _('Outro')),
    )
    
    candidate = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='talent_profile',
        verbose_name=_('Candidato')
    )
    pools = models.ManyToManyField(
        TalentPool, 
        related_name='talents',
        blank=True,
        verbose_name=_('Bancos de Talentos')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        verbose_name=_('Status')
    )
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES, 
        default='application',
        verbose_name=_('Origem')
    )
    notes_content = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Observações')
    )
    skills = models.ManyToManyField(
        Skill, 
        through='TalentSkill',
        related_name='talents',
        verbose_name=_('Habilidades')
    )
    departments_of_interest = models.ManyToManyField(
        Department, 
        related_name='interested_talents',
        blank=True,
        verbose_name=_('Departamentos de Interesse')
    )
    salary_expectation_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True, 
        null=True,
        verbose_name=_('Expectativa Salarial Mínima')
    )
    salary_expectation_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True, 
        null=True,
        verbose_name=_('Expectativa Salarial Máxima')
    )
    available_start_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_('Data de Disponibilidade')
    )
    last_contact_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_('Data do Último Contato')
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
        verbose_name = _('Talento')
        verbose_name_plural = _('Talentos')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Talento: {self.candidate.user.get_full_name()}"
    
    @property
    def full_name(self):
        """Retorna o nome completo do candidato."""
        return self.candidate.user.get_full_name()
    
    @property
    def email(self):
        """Retorna o email do candidato."""
        return self.candidate.user.email
    
    @property
    def phone(self):
        """Retorna o telefone do candidato."""
        return self.candidate.phone
    
    @property
    def days_since_last_contact(self):
        """Calcula o número de dias desde o último contato."""
        if self.last_contact_date:
            return (timezone.now().date() - self.last_contact_date).days
        return None


class TalentSkill(models.Model):
    """
    Modelo para relacionamento entre talentos e habilidades, com nível de proficiência.
    """
    talent = models.ForeignKey(
        'Talent',
        on_delete=models.CASCADE,
        related_name='talent_notes_set',  # Nome único e específico
        related_query_name='talent_note',  # Nome único para queries
        verbose_name=_('Talento')
    )
    skill = models.ForeignKey(
        Skill, 
        on_delete=models.CASCADE,
        related_name='talent_skills',
        verbose_name=_('Habilidade')
    )
    proficiency = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        verbose_name=_('Nível de Proficiência')
    )
    years_experience = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        default=0,
        verbose_name=_('Anos de Experiência')
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Habilidade Principal')
    )
    
    class Meta:
        verbose_name = _('Habilidade do Talento')
        verbose_name_plural = _('Habilidades dos Talentos')
        unique_together = ('talent', 'skill')
    
    def __str__(self):
        return f"{self.talent.candidate.user.get_full_name()} - {self.skill.name} (Nível {self.proficiency})"


class Tag(models.Model):
    """
    Modelo para tags de categorização de talentos.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_('Cor')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='tags_created',
        verbose_name=_('Criado por')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TalentTag(models.Model):
    """
    Modelo para relacionamento entre talentos e tags.
    """
    talent = models.ForeignKey(
        Talent, 
        on_delete=models.CASCADE,
        related_name='talent_tags',
        verbose_name=_('Talento')
    )
    tag = models.ForeignKey(
        Tag, 
        on_delete=models.CASCADE,
        related_name='talent_tags',
        verbose_name=_('Tag')
    )
    added_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='talent_tags_added',
        verbose_name=_('Adicionado por')
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Adição')
    )
    
    class Meta:
        verbose_name = _('Tag do Talento')
        verbose_name_plural = _('Tags dos Talentos')
        unique_together = ('talent', 'tag')
    
    def __str__(self):
        return f"{self.talent.candidate.user.get_full_name()} - {self.tag.name}"


class TalentNote(models.Model):
    """
    Modelo para anotações sobre talentos.
    """
    talent = models.ForeignKey(
        Talent, 
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Talento')
    )
    author = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='talent_notes_created',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Conteúdo')
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
        verbose_name = _('Anotação sobre Talento')
        verbose_name_plural = _('Anotações sobre Talentos')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Nota sobre {self.talent.candidate.user.get_full_name()} por {self.author.user.get_full_name() if self.author else 'Desconhecido'}"


class SavedSearch(models.Model):
    """
    Modelo para buscas salvas no banco de talentos.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    owner = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='saved_searches',
        verbose_name=_('Proprietário')
    )
    query_params = models.JSONField(
        verbose_name=_('Parâmetros da Busca')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Pública')
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
        verbose_name = _('Busca Salva')
        verbose_name_plural = _('Buscas Salvas')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.owner.user.get_full_name()}"


class TalentRecommendation(models.Model):
    """
    Modelo para recomendações de talentos para vagas.
    """
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('contacted', _('Contatado')),
        ('interested', _('Interessado')),
        ('not_interested', _('Não Interessado')),
        ('applied', _('Candidatou-se')),
    )
    
    talent = models.ForeignKey(
        Talent, 
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('Talento')
    )
    vacancy = models.ForeignKey(
        Vacancy, 
        on_delete=models.CASCADE,
        related_name='talent_recommendations',
        verbose_name=_('Vaga')
    )
    recommender = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='recommendations_made',
        verbose_name=_('Recomendado por')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    notes_content = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Observações')
    )
    match_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name=_('Pontuação de Compatibilidade')
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
        verbose_name = _('Recomendação de Talento')
        verbose_name_plural = _('Recomendações de Talentos')
        unique_together = ('talent', 'vacancy')
        ordering = ['-match_score']
    
    def __str__(self):
        return f"{self.talent.candidate.user.get_full_name()} para {self.vacancy.title} ({self.match_score}%)"
