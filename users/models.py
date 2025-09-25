from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings



class CustomUserManager(BaseUserManager):
    """Define um gerenciador de modelo para usuário customizado sem username."""

    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError(_('O email é obrigatório'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário precisa ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário precisa ter is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Modelo de usuário customizado que usa email em vez de username."""

    CANDIDATE = 'candidate'
    RECRUITER = 'recruiter'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (CANDIDATE, _('Candidato')),
        (RECRUITER, _('Recrutador')),
        (ADMIN, _('Administrador')),
    )

    username = None
    email = models.EmailField(_('endereço de email'), unique=True)
    first_name = models.CharField(_('nome'), max_length=150)
    last_name = models.CharField(_('sobrenome'), max_length=150)
    role = models.CharField(_('perfil'), max_length=20, choices=ROLE_CHOICES, default=CANDIDATE)
    phone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(_('data de nascimento'), blank=True, null=True)
    profile_picture = models.ImageField(_('foto de perfil'), upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(_('biografia'), blank=True, null=True)
    
    # Campos específicos para candidatos
    cpf = models.CharField(_('CPF'), max_length=14, blank=True, null=True)
    address = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True, null=True)
    state = models.CharField(_('estado'), max_length=2, blank=True, null=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    
    # Campos adicionais para perfil completo
    nome_social = models.CharField(_('nome social'), max_length=150, blank=True, null=True)
    pis = models.CharField(_('PIS'), max_length=20, blank=True, null=True)
    rg = models.CharField(_('RG'), max_length=20, blank=True, null=True)
    rg_emissao = models.DateField(_('data de emissão RG'), blank=True, null=True)
    rg_orgao = models.CharField(_('órgão emissor RG'), max_length=50, blank=True, null=True)
    
    # Raça/Cor com opções específicas
    RACA_COR_CHOICES = [
        ('indigena', 'Indígena'),
        ('branca', 'Branca'),
        ('preta', 'Preta'),
        ('amarela', 'Amarela'),
        ('parda', 'Parda'),
    ]
    raca_cor = models.CharField(_('raça/cor'), max_length=20, choices=RACA_COR_CHOICES, blank=True, null=True)
    
    # Sexo (designação ao nascer)
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    sexo = models.CharField(_('sexo (designação ao nascer)'), max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    
    # Gênero com opções específicas
    GENERO_CHOICES = [
        ('homem_cis', 'Homem Cisgênero'),
        ('homem_trans', 'Homem Transexual/Transgênero'),
        ('mulher_cis', 'Mulher Cisgênero'),
        ('mulher_trans', 'Mulher Transexual/Transgênero'),
        ('nao_binario', 'Não-binário'),
        ('outros', 'Outros'),
        ('prefiro_nao_responder', 'Prefiro não responder'),
    ]
    genero = models.CharField(_('gênero'), max_length=30, choices=GENERO_CHOICES, blank=True, null=True)
    
    # Estado civil com opções específicas
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('uniao_estavel', 'União Estável'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
    ]
    estado_civil = models.CharField(_('estado civil'), max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)
    
    # Telefone com WhatsApp
    whatsapp = models.CharField(_('telefone com WhatsApp'), max_length=20, blank=True, null=True)
    
    # Confirmação de email
    email_confirmado = models.BooleanField(_('email confirmado'), default=False)
    
    # Endereço completo
    numero = models.CharField(_('número'), max_length=10, blank=True, null=True)
    complemento = models.CharField(_('complemento'), max_length=100, blank=True, null=True)
    bairro = models.CharField(_('bairro'), max_length=100, blank=True, null=True)
    
    # Configurações de notificação e privacidade
    notificacoes_email = models.BooleanField(_('notificações por email'), default=True)
    notificacoes_sms = models.BooleanField(_('notificações por SMS'), default=False)
    perfil_visivel = models.BooleanField(_('perfil visível'), default=True)
    compartilhar_dados = models.BooleanField(_('compartilhar dados'), default=False)
    perfil_publico = models.BooleanField(_('perfil público'), default=False)
    receber_convites = models.BooleanField(_('receber convites'), default=True)
    
    # Campos específicos para recrutadores
    department = models.CharField(_('departamento'), max_length=100, blank=True, null=True)
    position = models.CharField(_('cargo'), max_length=100, blank=True, null=True)
    employee_id = models.CharField(_('ID de funcionário'), max_length=20, blank=True, null=True)
    
    # Campos de controle
    is_active = models.BooleanField(_('ativo'), default=True)
    is_staff = models.BooleanField(_('equipe'), default=False)
    date_joined = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    last_login = models.DateTimeField(_('último login'), auto_now=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Retorna o primeiro nome do usuário."""
        return self.first_name

    @property
    def is_candidate(self):
        """Verifica se o usuário é um candidato."""
        return self.role == self.CANDIDATE

    @property
    def is_recruiter(self):
        """Verifica se o usuário é um recrutador."""
        return self.role == self.RECRUITER

    @property
    def is_admin(self):
        """Verifica se o usuário é um administrador."""
        return self.role == self.ADMIN
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='user_custom_set',  # Adicione esta linha
        related_query_name='user_custom',  # Adicione esta linha
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='user_custom_set',  # Adicione esta linha
        related_query_name='user_custom',  # Adicione esta linha
    )


class CandidateProfile(models.Model):
    """Perfil estendido para candidatos."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    
    # Campos básicos do perfil
    education_level = models.CharField(_('nível de escolaridade'), max_length=50, blank=True, null=True)
    course = models.CharField(_('curso'), max_length=100, blank=True, null=True)
    institution = models.CharField(_('instituição'), max_length=100, blank=True, null=True)
    graduation_year = models.IntegerField(_('ano de conclusão'), blank=True, null=True)
    
    # Campos de experiência
    current_company = models.CharField(_('empresa atual'), max_length=100, blank=True, null=True)
    current_position = models.CharField(_('cargo atual'), max_length=100, blank=True, null=True)
    experience_years = models.CharField(_('tempo de experiência'), max_length=50, blank=True, null=True)
    
    # Campos de endereço
    address = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True, null=True)
    state = models.CharField(_('estado'), max_length=2, blank=True, null=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    
    # Campos de contato
    phone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    
    # Campos de identificação
    cpf = models.CharField(_('CPF'), max_length=14, blank=True, null=True)
    rg = models.CharField(_('RG'), max_length=20, blank=True, null=True)
    pis = models.CharField(_('PIS'), max_length=20, blank=True, null=True)
    
    # Campos de perfil
    bio = models.TextField(_('biografia'), blank=True, null=True)
    profile_picture = models.ImageField(_('foto de perfil'), upload_to='profile_pictures/', blank=True, null=True)
    
    # Campos de configuração
    is_public = models.BooleanField(_('perfil público'), default=False)
    share_data = models.BooleanField(_('compartilhar dados'), default=False)
    
    created_at = models.DateTimeField(_('data de criação'), auto_now_add=True)
    updated_at = models.DateTimeField(_('data de atualização'), auto_now=True)
    
    class Meta:
        verbose_name = _('perfil de candidato')
        verbose_name_plural = _('perfis de candidatos')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


# Modelos para as seções do currículo
class Education(models.Model):
    """Formação Acadêmica"""
    
    NIVEL_CHOICES = [
        ('fundamental_incompleto', 'Ensino Fundamental Incompleto'),
        ('fundamental_completo', 'Ensino Fundamental Completo'),
        ('medio_incompleto', 'Ensino Médio Incompleto'),
        ('medio_completo', 'Ensino Médio Completo'),
        ('tecnico', 'Técnico'),
        ('superior_incompleto', 'Superior Incompleto'),
        ('superior_completo', 'Superior Completo'),
        ('pos_graduacao', 'Pós-graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    instituicao = models.CharField(_('instituição'), max_length=200)
    curso = models.CharField(_('curso'), max_length=200)
    nivel = models.CharField(_('nível'), max_length=50, choices=NIVEL_CHOICES)
    inicio = models.DateField(_('data de início'))
    fim = models.DateField(_('data de conclusão'), blank=True, null=True)
    em_andamento = models.BooleanField(_('em andamento'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('formação acadêmica')
        verbose_name_plural = _('formações acadêmicas')
        ordering = ['-fim', '-inicio']
    
    def __str__(self):
        return f"{self.curso} - {self.instituicao}"


class Experience(models.Model):
    """Experiência Profissional"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experiences')
    empresa = models.CharField(_('empresa'), max_length=200)
    cargo = models.CharField(_('cargo'), max_length=200)
    inicio = models.DateField(_('data de início'))
    fim = models.DateField(_('data de saída'), blank=True, null=True)
    atual = models.BooleanField(_('trabalho atual'), default=False)
    atividades = models.TextField(_('atividades e responsabilidades'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('experiência profissional')
        verbose_name_plural = _('experiências profissionais')
        ordering = ['-fim', '-inicio']
    
    def __str__(self):
        return f"{self.cargo} - {self.empresa}"


class TechnicalSkill(models.Model):
    """Habilidades Técnicas"""
    
    NIVEL_CHOICES = [
        ('basico', 'Básico'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('expert', 'Expert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='technical_skills')
    nome = models.CharField(_('nome da habilidade'), max_length=100)
    nivel = models.CharField(_('nível'), max_length=20, choices=NIVEL_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('habilidade técnica')
        verbose_name_plural = _('habilidades técnicas')
        ordering = ['nome']
        unique_together = ['user', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_nivel_display()})"


class SoftSkill(models.Model):
    """Habilidades Emocionais"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='soft_skills')
    nome = models.CharField(_('nome da habilidade'), max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('habilidade emocional')
        verbose_name_plural = _('habilidades emocionais')
        ordering = ['nome']
        unique_together = ['user', 'nome']
    
    def __str__(self):
        return self.nome


class Certification(models.Model):
    """Certificações"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certifications')
    titulo = models.CharField(_('título'), max_length=200)
    orgao = models.CharField(_('órgão emissor'), max_length=200, blank=True)
    emissao = models.DateField(_('data de emissão'), blank=True, null=True)
    validade = models.DateField(_('data de validade'), blank=True, null=True)
    sem_validade = models.BooleanField(_('sem data de validade'), default=False)
    credencial_url = models.URLField(_('URL da credencial'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('certificação')
        verbose_name_plural = _('certificações')
        ordering = ['titulo']
    
    def __str__(self):
        return self.titulo


class Language(models.Model):
    """Idiomas"""
    
    IDIOMA_CHOICES = [
        ('portugues', 'Português'),
        ('ingles', 'Inglês'),
        ('espanhol', 'Espanhol'),
        ('frances', 'Francês'),
        ('alemao', 'Alemão'),
        ('italiano', 'Italiano'),
        ('japones', 'Japonês'),
        ('chines', 'Chinês'),
        ('coreano', 'Coreano'),
        ('russo', 'Russo'),
        ('arabe', 'Árabe'),
        ('outro', 'Outro'),
    ]
    
    NIVEL_CHOICES = [
        ('basico', 'Básico'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
        ('fluente', 'Fluente'),
        ('nativo', 'Nativo'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='languages')
    idioma = models.CharField(_('idioma'), max_length=50, choices=IDIOMA_CHOICES)
    idioma_outro = models.CharField(_('outro idioma'), max_length=100, blank=True, null=True)
    nivel = models.CharField(_('nível'), max_length=20, choices=NIVEL_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('idioma')
        verbose_name_plural = _('idiomas')
        ordering = ['idioma']
        unique_together = ['user', 'idioma']
    
    def __str__(self):
        if self.idioma == 'outro' and self.idioma_outro:
            return f"{self.idioma_outro} ({self.get_nivel_display()})"
        return f"{self.get_idioma_display()} ({self.get_nivel_display()})"


class RecruiterProfile(models.Model):
    """Perfil estendido para recrutadores."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    
    # Informações profissionais
    specialization = models.CharField(_('especialização'), max_length=100, blank=True, null=True)
    hiring_authority = models.BooleanField(_('autoridade para contratar'), default=False)
    
    # Estatísticas
    vacancies_created = models.IntegerField(_('vagas criadas'), default=0)
    candidates_interviewed = models.IntegerField(_('candidatos entrevistados'), default=0)
    successful_hires = models.IntegerField(_('contratações bem-sucedidas'), default=0)
    
    # Preferências
    notification_preferences = models.JSONField(_('preferências de notificação'), default=dict)
    
    # Metadados
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('perfil de recrutador')
        verbose_name_plural = _('perfis de recrutadores')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"

class UserProfile(models.Model):
    """Modelo de compatibilidade para integração com o código existente."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    class Meta:
        verbose_name = _('perfil de usuário')
        verbose_name_plural = _('perfis de usuários')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
    
    # Métodos para compatibilidade com o código existente
    @property
    def is_candidate(self):
        return self.user.is_candidate
    
    @property
    def is_recruiter(self):
        return self.user.is_recruiter
    
    @property
    def is_admin(self):
        return self.user.is_admin
    
    @property
    def candidate_profile(self):
        if hasattr(self.user, 'candidate_profile'):
            return self.user.candidate_profile
        return None
    
    @property
    def recruiter_profile(self):
        if hasattr(self.user, 'recruiter_profile'):
            return self.user.recruiter_profile
        return None
    
    # Método para compatibilidade
    def get_full_name(self):
        return self.user.get_full_name()


# Signals para criar automaticamente um UserProfile quando um User for criado
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria um UserProfile automaticamente quando um User é criado."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o UserProfile quando o User é salvo."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
