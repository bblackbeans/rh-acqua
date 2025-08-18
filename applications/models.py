from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import UserProfile
from vacancies.models import Vacancy


class Application(models.Model):
    """
    Modelo para candidaturas a vagas.
    """
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('under_review', _('Em Análise')),
        ('interview', _('Entrevista')),
        ('approved', _('Aprovado')),
        ('rejected', _('Rejeitado')),
        ('withdrawn', _('Desistência')),
    )

    candidate = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name=_('Candidato')
    )
    vacancy = models.ForeignKey(
        Vacancy, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name=_('Vaga')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    cover_letter = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Carta de Apresentação')
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True, 
        null=True,
        verbose_name=_('Currículo')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    recruiter_notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Notas do Recrutador')
    )
    
    class Meta:
        verbose_name = _('Candidatura')
        verbose_name_plural = _('Candidaturas')
        ordering = ['-created_at']
        unique_together = ('candidate', 'vacancy')
    
    def __str__(self):
        return f"{self.candidate.user.get_full_name()} - {self.vacancy.title}"
    
    def get_status_display_class(self):
        """Retorna uma classe CSS baseada no status atual."""
        status_classes = {
            'pending': 'badge-secondary',
            'under_review': 'badge-primary',
            'interview': 'badge-info',
            'approved': 'badge-success',
            'rejected': 'badge-danger',
            'withdrawn': 'badge-warning',
        }
        return status_classes.get(self.status, 'badge-secondary')


class ApplicationEvaluation(models.Model):
    """
    Modelo para avaliação de candidaturas por recrutadores.
    """
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='evaluations',
        verbose_name=_('Candidatura')
    )
    evaluator = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='evaluations_made',
        verbose_name=_('Avaliador')
    )
    technical_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Pontuação Técnica')
    )
    experience_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Pontuação de Experiência')
    )
    cultural_fit_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Adequação Cultural')
    )
    comments = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Comentários')
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
        verbose_name = _('Avaliação de Candidatura')
        verbose_name_plural = _('Avaliações de Candidaturas')
        ordering = ['-created_at']
        unique_together = ('application', 'evaluator')
    
    def __str__(self):
        return f"Avaliação: {self.application} por {self.evaluator.user.get_full_name()}"
    
    @property
    def total_score(self):
        """Calcula a pontuação total da avaliação."""
        return self.technical_score + self.experience_score + self.cultural_fit_score
    
    @property
    def average_score(self):
        """Calcula a pontuação média da avaliação."""
        return self.total_score / 3


class Resume(models.Model):
    """
    Modelo para currículos detalhados dos candidatos.
    """
    candidate = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='detailed_resume',
        verbose_name=_('Candidato')
    )
    summary = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Resumo Profissional')
    )
    skills = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Habilidades')
    )
    languages = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Idiomas')
    )
    certifications = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Certificações')
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
        verbose_name = _('Currículo Detalhado')
        verbose_name_plural = _('Currículos Detalhados')
    
    def __str__(self):
        return f"Currículo de {self.candidate.user.get_full_name()}"


class Education(models.Model):
    """
    Modelo para formação educacional no currículo.
    """
    DEGREE_CHOICES = (
        ('high_school', _('Ensino Médio')),
        ('technical', _('Curso Técnico')),
        ('bachelor', _('Graduação')),
        ('specialization', _('Especialização')),
        ('mba', _('MBA')),
        ('master', _('Mestrado')),
        ('doctorate', _('Doutorado')),
        ('post_doctorate', _('Pós-Doutorado')),
        ('other', _('Outro')),
    )
    
    resume = models.ForeignKey(
        Resume, 
        on_delete=models.CASCADE, 
        related_name='education',
        verbose_name=_('Currículo')
    )
    institution = models.CharField(
        max_length=255,
        verbose_name=_('Instituição')
    )
    degree = models.CharField(
        max_length=20, 
        choices=DEGREE_CHOICES,
        verbose_name=_('Grau')
    )
    field_of_study = models.CharField(
        max_length=255,
        verbose_name=_('Área de Estudo')
    )
    start_date = models.DateField(
        verbose_name=_('Data de Início')
    )
    end_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_('Data de Conclusão')
    )
    is_current = models.BooleanField(
        default=False,
        verbose_name=_('Cursando Atualmente')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    
    class Meta:
        verbose_name = _('Formação Educacional')
        verbose_name_plural = _('Formações Educacionais')
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.get_degree_display()} em {self.field_of_study} - {self.institution}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)


class WorkExperience(models.Model):
    """
    Modelo para experiências profissionais no currículo.
    """
    resume = models.ForeignKey(
        Resume, 
        on_delete=models.CASCADE, 
        related_name='work_experiences',
        verbose_name=_('Currículo')
    )
    company = models.CharField(
        max_length=255,
        verbose_name=_('Empresa')
    )
    position = models.CharField(
        max_length=255,
        verbose_name=_('Cargo')
    )
    start_date = models.DateField(
        verbose_name=_('Data de Início')
    )
    end_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_('Data de Término')
    )
    is_current = models.BooleanField(
        default=False,
        verbose_name=_('Trabalho Atual')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    achievements = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Realizações')
    )
    
    class Meta:
        verbose_name = _('Experiência Profissional')
        verbose_name_plural = _('Experiências Profissionais')
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.position} em {self.company}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Calcula a duração da experiência em meses."""
        end = self.end_date or timezone.now().date()
        start = self.start_date
        
        # Cálculo aproximado de meses
        months = (end.year - start.year) * 12 + (end.month - start.month)
        return months


class ApplicationComplementaryInfo(models.Model):
    """
    Modelo para informações complementares da candidatura.
    """
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='complementary_info',
        verbose_name=_('Candidatura')
    )
    
    # Histórico Profissional
    trabalha_atualmente = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name=_('Trabalha atualmente no hospital/unidade')
    )
    funcao_atual = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Função atual')
    )
    experiencia_area = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name=_('Possui experiência na área da vaga')
    )
    descricao_experiencia = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descrição da experiência na área')
    )
    ultima_funcao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Última função exercida')
    )
    tempo_experiencia = models.CharField(
        max_length=20,
        choices=[
            ('menos_6_meses', 'Menos de 6 meses'),
            ('6_meses_1_ano', '6 meses a 1 ano'),
            ('1_2_anos', '1 a 2 anos'),
            ('2_5_anos', '2 a 5 anos'),
            ('acima_5_anos', 'Acima de 5 anos'),
        ],
        verbose_name=_('Tempo de experiência')
    )
    
    # Disponibilidade
    disponibilidade_manha = models.BooleanField(default=False, verbose_name=_('Disponibilidade Manhã'))
    disponibilidade_tarde = models.BooleanField(default=False, verbose_name=_('Disponibilidade Tarde'))
    disponibilidade_noite = models.BooleanField(default=False, verbose_name=_('Disponibilidade Noite'))
    disponibilidade_comercial = models.BooleanField(default=False, verbose_name=_('Disponibilidade Horário Comercial'))
    disponibilidade_plantao_dia = models.BooleanField(default=False, verbose_name=_('Disponibilidade Plantão 12x36 (dia)'))
    disponibilidade_plantao_noite = models.BooleanField(default=False, verbose_name=_('Disponibilidade Plantão 12x36 (noite)'))
    inicio_imediato = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name=_('Disponibilidade para início imediato')
    )
    
    # Informações Complementares
    trabalhou_acqua = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name=_('Já trabalhou no Instituto ACQUA')
    )
    area_cargo_acqua = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Área/Cargo no ACQUA')
    )
    data_desligamento = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Data de desligamento do ACQUA')
    )
    parentes_instituicao = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name=_('Possui parentes na instituição')
    )
    grau_parentesco = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('avo', 'Avô (a)'),
            ('pai', 'Pai'),
            ('mae', 'Mãe'),
            ('filho', 'Filho (a)'),
            ('irmao', 'Irmão (a)'),
            ('tio', 'Tio (a)'),
            ('sobrinho', 'Sobrinho (a)'),
            ('primo', 'Primo (a)'),
            ('conjuge', 'Cônjuge'),
            ('enteado', 'Enteado (a)'),
            ('sogro', 'Sogro (a)'),
            ('genro', 'Genro'),
            ('nora', 'Nora'),
            ('neto', 'Neto (a)'),
            ('cunhado', 'Cunhado (a)'),
            ('nenhum', 'Nenhum'),
        ],
        verbose_name=_('Grau de parentesco')
    )
    nome_parente_setor = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Nome do parente e setor')
    )
    
    # Declarações
    declaracao_veracidade = models.BooleanField(default=False, verbose_name=_('Declaração de veracidade'))
    declaracao_edital = models.BooleanField(default=False, verbose_name=_('Declaração de concordância com edital'))
    autorizacao_dados = models.BooleanField(default=False, verbose_name=_('Autorização de uso de dados'))
    data_declaracao = models.CharField(
        max_length=10,
        verbose_name=_('Data da declaração')
    )
    
    # NOVO: PCD
    is_pcd = models.CharField(max_length=3, choices=[('sim','Sim'),('nao','Não')], blank=True, null=True, verbose_name=_('É PCD'))
    cid = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('CID'))
    atestado_pcd = models.FileField(upload_to='pcd_atestados/', blank=True, null=True, verbose_name=_('Atestado PCD'))
    necessita_adaptacoes = models.CharField(max_length=3, choices=[('sim','Sim'),('nao','Não')], blank=True, null=True, verbose_name=_('Necessita adaptações'))
    descricao_adaptacoes = models.TextField(blank=True, null=True, verbose_name=_('Descrição das adaptações'))
    
    # NOVO: Conselho Regional
    conselho_regional = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Conselho regional'))
    numero_registro = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Número do registro'))
    validade_registro = models.DateField(blank=True, null=True, verbose_name=_('Validade do registro'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de criação'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Data de atualização'))
    
    class Meta:
        verbose_name = _('Informação Complementar da Candidatura')
        verbose_name_plural = _('Informações Complementares das Candidaturas')
    
    def __str__(self):
        return f"Informações complementares - {self.application}"
