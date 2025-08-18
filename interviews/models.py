from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import UserProfile
from applications.models import Application


class Interview(models.Model):
    """
    Modelo para entrevistas de candidatos.
    """
    TYPE_CHOICES = (
        ('presential', _('Presencial')),
        ('video', _('Vídeo')),
        ('phone', _('Telefone')),
        ('group', _('Dinâmica em Grupo')),
        ('technical', _('Técnica')),
    )
    
    STATUS_CHOICES = (
        ('scheduled', _('Agendada')),
        ('confirmed', _('Confirmada')),
        ('completed', _('Realizada')),
        ('canceled', _('Cancelada')),
        ('rescheduled', _('Reagendada')),
        ('no_show', _('Não Compareceu')),
    )
    
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='interviews',
        verbose_name=_('Candidatura')
    )
    interviewer = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='interviews_conducted',
        verbose_name=_('Entrevistador')
    )
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='presential',
        verbose_name=_('Tipo')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled',
        verbose_name=_('Status')
    )
    scheduled_date = models.DateTimeField(
        verbose_name=_('Data Agendada')
    )
    duration = models.PositiveIntegerField(
        default=60,
        help_text=_('Duração em minutos'),
        verbose_name=_('Duração')
    )
    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name=_('Local')
    )
    meeting_link = models.URLField(
        blank=True, 
        null=True,
        verbose_name=_('Link da Reunião')
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Observações')
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
        verbose_name = _('Entrevista')
        verbose_name_plural = _('Entrevistas')
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.application.candidate.user.get_full_name()} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def candidate(self):
        """Retorna o candidato associado à entrevista."""
        return self.application.candidate
    
    @property
    def vacancy(self):
        """Retorna a vaga associada à entrevista."""
        return self.application.vacancy
    
    @property
    def is_past_due(self):
        """Verifica se a entrevista já passou."""
        return timezone.now() > self.scheduled_date
    
    @property
    def is_today(self):
        """Verifica se a entrevista é hoje."""
        return timezone.now().date() == self.scheduled_date.date()
    
    @property
    def time_until(self):
        """Retorna o tempo até a entrevista."""
        if self.is_past_due:
            return None
        return self.scheduled_date - timezone.now()


class InterviewFeedback(models.Model):
    """
    Modelo para feedback de entrevistas.
    """
    interview = models.OneToOneField(
        Interview, 
        on_delete=models.CASCADE, 
        related_name='feedback',
        verbose_name=_('Entrevista')
    )
    technical_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Pontuação Técnica')
    )
    communication_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Pontuação de Comunicação')
    )
    cultural_fit_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Adequação Cultural')
    )
    strengths = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Pontos Fortes')
    )
    weaknesses = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Pontos de Melhoria')
    )
    comments = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Comentários Gerais')
    )
    recommendation = models.CharField(
        max_length=20,
        choices=(
            ('hire', _('Contratar')),
            ('consider', _('Considerar')),
            ('reject', _('Rejeitar')),
            ('next_stage', _('Próxima Etapa')),
        ),
        verbose_name=_('Recomendação')
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
        verbose_name = _('Feedback de Entrevista')
        verbose_name_plural = _('Feedbacks de Entrevistas')
    
    def __str__(self):
        return f"Feedback - {self.interview}"
    
    @property
    def total_score(self):
        """Calcula a pontuação total do feedback."""
        return self.technical_score + self.communication_score + self.cultural_fit_score
    
    @property
    def average_score(self):
        """Calcula a pontuação média do feedback."""
        return self.total_score / 3


class InterviewQuestion(models.Model):
    """
    Modelo para perguntas de entrevista.
    """
    CATEGORY_CHOICES = (
        ('technical', _('Técnica')),
        ('behavioral', _('Comportamental')),
        ('experience', _('Experiência')),
        ('situational', _('Situacional')),
        ('cultural', _('Cultural')),
        ('other', _('Outra')),
    )
    
    text = models.TextField(
        verbose_name=_('Pergunta')
    )
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        verbose_name=_('Categoria')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativa')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='questions_created',
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
        verbose_name = _('Pergunta de Entrevista')
        verbose_name_plural = _('Perguntas de Entrevista')
        ordering = ['category', 'text']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.text[:50]}..."


class InterviewTemplate(models.Model):
    """
    Modelo para templates de entrevista.
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
    questions = models.ManyToManyField(
        InterviewQuestion, 
        through='TemplateQuestion',
        related_name='templates',
        verbose_name=_('Perguntas')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='templates_created',
        verbose_name=_('Criado por')
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
        verbose_name = _('Template de Entrevista')
        verbose_name_plural = _('Templates de Entrevista')
    
    def __str__(self):
        return self.name


class TemplateQuestion(models.Model):
    """
    Modelo para relacionamento entre templates e perguntas.
    """
    template = models.ForeignKey(
        InterviewTemplate, 
        on_delete=models.CASCADE,
        verbose_name=_('Template')
    )
    question = models.ForeignKey(
        InterviewQuestion, 
        on_delete=models.CASCADE,
        verbose_name=_('Pergunta')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ordem')
    )
    
    class Meta:
        verbose_name = _('Pergunta do Template')
        verbose_name_plural = _('Perguntas do Template')
        ordering = ['order']
        unique_together = ('template', 'question')
    
    def __str__(self):
        return f"{self.template.name} - {self.question.text[:30]}..."


class InterviewSchedule(models.Model):
    """
    Modelo para disponibilidade de entrevistadores.
    """
    interviewer = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='interview_schedules',
        verbose_name=_('Entrevistador')
    )
    date = models.DateField(
        verbose_name=_('Data')
    )
    start_time = models.TimeField(
        verbose_name=_('Hora de Início')
    )
    end_time = models.TimeField(
        verbose_name=_('Hora de Término')
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name=_('Recorrente')
    )
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=(
            ('daily', _('Diário')),
            ('weekly', _('Semanal')),
            ('biweekly', _('Quinzenal')),
            ('monthly', _('Mensal')),
        ),
        blank=True, 
        null=True,
        verbose_name=_('Padrão de Recorrência')
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
        verbose_name = _('Disponibilidade para Entrevista')
        verbose_name_plural = _('Disponibilidades para Entrevista')
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.interviewer.user.get_full_name()} - {self.date.strftime('%d/%m/%Y')} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    @property
    def duration_minutes(self):
        """Calcula a duração em minutos."""
        start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
        end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds // 60
