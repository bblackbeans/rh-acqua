# 📋 DOCUMENTAÇÃO TÉCNICA - RH ACQUA V2

## 🏥 VISÃO GERAL
Sistema completo de Recrutamento e Seleção para o setor hospitalar/saúde, desenvolvido em Django com arquitetura moderna e funcionalidades avançadas.

## 🏗️ ARQUITETURA TÉCNICA

### Stack Tecnológico
- **Backend:** Django 4.2.7 + Python
- **Frontend:** Bootstrap 5 + jQuery + Font Awesome
- **API:** Django REST Framework + Swagger/OpenAPI
- **Banco:** SQLite (desenvolvimento) / MySQL (produção)
- **Autenticação:** Sistema customizado com email como username
- **Templates:** Sistema de templates Django com componentes reutilizáveis

### Apps Principais
1. **`core`** - Funcionalidades centrais e base
2. **`users`** - Gestão de usuários e perfis
3. **`vacancies`** - Gestão de vagas e oportunidades
4. **`applications`** - Candidaturas e currículos
5. **`interviews`** - Entrevistas e avaliações
6. **`talent_pool`** - Banco de talentos
7. **`notifications`** - Sistema de notificações
8. **`reports`** - Relatórios e analytics
9. **`administration`** - Configurações e administração
10. **`api`** - API REST
11. **`utils`** - Utilitários e helpers

## ⚙️ CONFIGURAÇÕES TÉCNICAS CRÍTICAS

### Configurações Django (settings.py)
```python
# Configurações principais
SECRET_KEY = 'django-insecure-q7bz=a0alipp(olr^#8en!13(va!mt%!4=)-a3$=25ha=#f-bv'
DEBUG = True
ALLOWED_HOSTS = []

# Apps instalados (ordem importante)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    
    # Apps do projeto (ordem de dependência)
    'core',           # Base e funcionalidades centrais
    'users',          # Sistema de usuários
    'vacancies',      # Gestão de vagas
    'applications',   # Candidaturas
    'interviews',     # Entrevistas
    'talent_pool',    # Banco de talentos
    'notifications',  # Sistema de notificações
    'reports',        # Relatórios
    'administration', # Administração
    'utils',          # Utilitários
    'api',            # API REST
    'templates',      # Templates customizados
    'hr_system',      # Configurações do projeto
]

# Middleware (ordem crítica)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Deve vir primeiro
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configurações de arquivos estáticos e mídia
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# URLs de redirecionamento
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configurações CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Configurações DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
```

## 👤 SISTEMA DE USUÁRIOS - DETALHES TÉCNICOS

### Modelo de Usuário Customizado
```python
# users/models.py
class User(AbstractUser):
    CANDIDATE = 'candidate'
    RECRUITER = 'recruiter'
    ADMIN = 'admin'
    
    ROLE_CHOICES = (
        (CANDIDATE, _('Candidato')),
        (RECRUITER, _('Recrutador')),
        (ADMIN, _('Administrador')),
    )
    
    username = None  # Remove username padrão
    email = models.EmailField(_('endereço de email'), unique=True)
    first_name = models.CharField(_('nome'), max_length=150)
    last_name = models.CharField(_('sobrenome'), max_length=150)
    role = models.CharField(_('perfil'), max_length=20, choices=ROLE_CHOICES, default=CANDIDATE)
    
    # Campos específicos para candidatos
    cpf = models.CharField(_('CPF'), max_length=14, blank=True, null=True)
    address = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True, null=True)
    state = models.CharField(_('estado'), max_length=2, blank=True, null=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    
    # Campos específicos para recrutadores
    department = models.CharField(_('departamento'), max_length=100, blank=True, null=True)
    position = models.CharField(_('cargo'), max_length=100, blank=True, null=True)
    employee_id = models.CharField(_('ID de funcionário'), max_length=20, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
```

### Perfis Estendidos
```python
# Perfil de Candidato
class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    education_level = models.CharField(_('nível de escolaridade'), max_length=50, blank=True, null=True)
    institution = models.CharField(_('instituição'), max_length=100, blank=True, null=True)
    course = models.CharField(_('curso'), max_length=100, blank=True, null=True)
    graduation_year = models.IntegerField(_('ano de formação'), blank=True, null=True)
    years_of_experience = models.IntegerField(_('anos de experiência'), default=0)
    current_position = models.CharField(_('cargo atual'), max_length=100, blank=True, null=True)
    current_company = models.CharField(_('empresa atual'), max_length=100, blank=True, null=True)
    skills = models.TextField(_('habilidades'), blank=True, null=True)
    desired_position = models.CharField(_('cargo desejado'), max_length=100, blank=True, null=True)
    desired_salary = models.DecimalField(_('salário desejado'), max_digits=10, decimal_places=2, blank=True, null=True)
    available_immediately = models.BooleanField(_('disponível imediatamente'), default=True)
    notice_period = models.IntegerField(_('período de aviso prévio (dias)'), default=0)
    resume = models.FileField(_('currículo'), upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(_('carta de apresentação'), blank=True, null=True)

# Perfil de Recrutador
class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    specialization = models.CharField(_('especialização'), max_length=100, blank=True, null=True)
    hiring_authority = models.BooleanField(_('autoridade para contratar'), default=False)
    vacancies_created = models.IntegerField(_('vagas criadas'), default=0)
    candidates_interviewed = models.IntegerField(_('candidatos entrevistados'), default=0)
    successful_hires = models.IntegerField(_('contratações bem-sucedidas'), default=0)
    notification_preferences = models.JSONField(_('preferências de notificação'), default=dict)
```

### Signals Automáticos
```python
# users/signals.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil baseado no role"""
    if created:
        if instance.role == User.CANDIDATE:
            CandidateProfile.objects.create(user=instance)
        elif instance.role == User.RECRUITER:
            RecruiterProfile.objects.create(user=instance)
```

## 🏥 MODELOS DE DADOS PRINCIPAIS

### Estrutura Hospitalar
```python
# vacancies/models.py
class Hospital(models.Model):
    name = models.CharField(_('nome'), max_length=200)
    address = models.CharField(_('endereço'), max_length=255)
    city = models.CharField(_('cidade'), max_length=100)
    state = models.CharField(_('estado'), max_length=2)
    zip_code = models.CharField(_('CEP'), max_length=10)
    phone = models.CharField(_('telefone'), max_length=20)
    email = models.EmailField(_('email'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    description = models.TextField(_('descrição'), blank=True, null=True)
    logo = models.ImageField(_('logo'), upload_to='hospital_logos/', blank=True, null=True)
    is_active = models.BooleanField(_('ativo'), default=True)

class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(_('ativo'), default=True)

class JobCategory(models.Model):
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    is_active = models.BooleanField(_('ativo'), default=True)

class Skill(models.Model):
    name = models.CharField(_('nome'), max_length=100)
    description = models.TextField(_('descrição'), blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='skills')
```

### Sistema de Vagas
```python
class Vacancy(models.Model):
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
    
    # Campos principais
    title = models.CharField(_('título'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=250, unique=True, blank=True)
    description = models.TextField(_('descrição'))
    requirements = models.TextField(_('requisitos'))
    benefits = models.TextField(_('benefícios'), blank=True, null=True)
    
    # Relacionamentos
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='vacancies')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='vacancies')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='vacancies')
    skills = models.ManyToManyField(Skill, related_name='vacancies')
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_vacancies')
    
    # Detalhes da vaga
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    contract_type = models.CharField(_('tipo de contrato'), max_length=20, choices=CONTRACT_TYPE_CHOICES, default=FULL_TIME)
    experience_level = models.CharField(_('nível de experiência'), max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default=MID)
    salary_range_min = models.DecimalField(_('faixa salarial mínima'), max_digits=10, decimal_places=2, blank=True, null=True)
    salary_range_max = models.DecimalField(_('faixa salarial máxima'), max_digits=10, decimal_places=2, blank=True, null=True)
    is_salary_visible = models.BooleanField(_('salário visível'), default=False)
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
```

## 📝 SISTEMA DE CANDIDATURAS

### Modelo de Candidatura
```python
# applications/models.py
class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('under_review', _('Em Análise')),
        ('interview', _('Entrevista')),
        ('approved', _('Aprovado')),
        ('rejected', _('Rejeitado')),
        ('withdrawn', _('Desistência')),
    )

    candidate = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='applications')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recruiter_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('candidate', 'vacancy')
```

### Avaliação de Candidaturas
```python
class ApplicationEvaluation(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations_made')
    technical_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    experience_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    cultural_fit_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('application', 'evaluator')
    
    @property
    def total_score(self):
        return self.technical_score + self.experience_score + self.cultural_fit_score
    
    @property
    def average_score(self):
        return self.total_score / 3
```

## 🎯 SISTEMA DE ENTREVISTAS

### Modelo de Entrevista
```python
# interviews/models.py
class Interview(models.Model):
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
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interviews_conducted')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='presential')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=60, help_text=_('Duração em minutos'))
    location = models.CharField(max_length=255, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def candidate(self):
        return self.application.candidate
    
    @property
    def vacancy(self):
        return self.application.vacancy
    
    @property
    def is_past_due(self):
        return timezone.now() > self.scheduled_date
    
    @property
    def is_today(self):
        return timezone.now().date() == self.scheduled_date.date()
```

### Feedback de Entrevista
```python
class InterviewFeedback(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='feedback')
    technical_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    communication_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    cultural_fit_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    recommendation = models.CharField(max_length=20, choices=(
        ('hire', _('Contratar')),
        ('consider', _('Considerar')),
        ('reject', _('Rejeitar')),
        ('next_stage', _('Próxima Etapa')),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_score(self):
        return self.technical_score + self.communication_score + self.cultural_fit_score
    
    @property
    def average_score(self):
        return self.total_score / 3
```

## 🌟 BANCO DE TALENTOS

### Modelo de Talento
```python
# talent_pool/models.py
class Talent(models.Model):
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
    
    candidate = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='talent_profile')
    pools = models.ManyToManyField(TalentPool, related_name='talents', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='application')
    notes_content = models.TextField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, through='TalentSkill', related_name='talents')
    departments_of_interest = models.ManyToManyField(Department, related_name='interested_talents', blank=True)
    salary_expectation_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_expectation_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_start_date = models.DateField(blank=True, null=True)
    last_contact_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def days_since_last_contact(self):
        if self.last_contact_date:
            return (timezone.now().date() - self.last_contact_date).days
        return None
```

## 🔔 SISTEMA DE NOTIFICAÇÕES

### Estrutura de Notificações
```python
# notifications/models.py
class Notification(models.Model):
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
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    url = models.CharField(max_length=255, blank=True)
    
    # Objeto relacionado (opcional)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(blank=True, null=True)
    
    # Datas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(blank=True, null=True)
```

## 📊 RELATÓRIOS E ANALYTICS

### Tipos de Relatórios Disponíveis
- **Funil de Recrutamento** - Conversão de candidatos por etapa
- **Tempo de Contratação** - Métricas de velocidade de contratação
- **Eficiência de Fontes** - Performance de diferentes canais
- **Desempenho de Entrevistadores** - Avaliação de entrevistadores
- **Status de Vagas** - Distribuição de vagas por status
- **Demografia de Candidatos** - Análise demográfica
- **Relatórios Personalizados** - Criação de relatórios customizados

### Funcionalidades de Relatórios
- Agendamento automático
- Múltiplos formatos (PDF, Excel, CSV, HTML)
- Dashboards personalizáveis
- Widgets configuráveis
- Métricas em tempo real
- Templates de relatórios

## 🔌 API REST

### Endpoints Principais
```
/api/
├── auth/
│   ├── login/
│   ├── logout/
│   └── password/change/
├── users/
├── vacancies/
├── applications/
├── interviews/
├── talent-pool/
├── reports/
├── notifications/
├── health/
├── docs/
├── swagger/
└── redoc/
```

### Configurações da API
- **Autenticação:** Session + Basic Authentication
- **Permissões:** IsAuthenticated por padrão
- **Paginação:** PageNumberPagination (20 itens por página)
- **Filtros:** DjangoFilterBackend + SearchFilter + OrderingFilter
- **Documentação:** Swagger/OpenAPI integrado

## 🛡️ SISTEMA DE PERMISSÕES

### Classes de Permissão
```python
# users/permissions.py
class IsOwnerOrAdmin(permissions.BasePermission):
    """Permite que apenas o proprietário ou admin modifique"""
    
class IsRecruiterOrAdmin(permissions.BasePermission):
    """Permite que apenas recrutadores ou admins acessem"""
    
class IsAdminUser(permissions.BasePermission):
    """Permite que apenas administradores acessem"""
```

### Controle de Acesso por Perfil
- **Candidatos:** Acesso limitado a suas próprias candidaturas
- **Recrutadores:** Acesso a vagas que criaram + candidatos
- **Administradores:** Acesso total ao sistema

## 🎨 INTERFACE DO USUÁRIO

### Estrutura de Templates
```
templates/
├── base.html                    # Template base
├── components/                  # Componentes reutilizáveis
│   ├── header.html
│   ├── footer.html
│   ├── sidebar/
│   ├── cards/
│   ├── forms/
│   ├── modals/
│   ├── tables/
│   └── widgets/
├── navigation/                  # Menus por perfil
│   ├── admin_menu.html
│   ├── recruiter_menu.html
│   └── candidate_menu.html
└── [app_name]/                  # Templates específicos por app
```

### Design System
- **Framework:** Bootstrap 5
- **Ícones:** Font Awesome 6.4.0
- **Fontes:** Google Fonts (Roboto)
- **Responsividade:** Mobile-first design
- **Componentes:** Modulares e reutilizáveis

## 🔧 UTILITÁRIOS IMPORTANTES

### Helpers Principais (utils/helpers.py)
```python
# Formatação de documentos brasileiros
format_cpf(cpf)           # Formata CPF (XXX.XXX.XXX-XX)
format_cnpj(cnpj)         # Formata CNPJ (XX.XXX.XXX/XXXX-XX)
format_cep(cep)           # Formata CEP (XXXXX-XXX)
format_phone(phone)       # Formata telefone brasileiro
format_currency(value)    # Formata valores monetários

# Validação
is_valid_cpf(cpf)         # Valida CPF
is_valid_cnpj(cnpj)       # Valida CNPJ

# Utilitários gerais
generate_unique_slug()    # Gera slugs únicos
truncate_string()         # Trunca strings
get_client_ip()           # Obtém IP do cliente
get_age_from_birth_date() # Calcula idade
get_time_ago()           # Tempo relativo
```

## 📋 COMANDOS ÚTEIS

### Desenvolvimento
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Produção
```bash
# Configurar banco MySQL
# Atualizar settings.py com configurações de produção
# Configurar SECRET_KEY
# Definir DEBUG = False
# Configurar ALLOWED_HOSTS
# Configurar STATIC_ROOT e MEDIA_ROOT
```

## 🚀 DEPLOYMENT

### Requisitos de Sistema
- **Python:** 3.8+
- **Django:** 4.2.7
- **Banco:** MySQL 5.7+ ou PostgreSQL 12+
- **Servidor:** Nginx + Gunicorn (recomendado)
- **Cache:** Redis (opcional)
- **Storage:** Sistema de arquivos ou S3

### Configurações de Produção
```python
# settings_production.py
DEBUG = False
ALLOWED_HOSTS = ['seudominio.com', 'www.seudominio.com']

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Configurações de banco
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rh_acqua_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🔍 TROUBLESHOOTING

### Problemas Comuns
1. **Erro de migração:** `python manage.py migrate --fake-initial`
2. **Arquivos estáticos não carregam:** `python manage.py collectstatic`
3. **Erro de permissão:** Verificar permissões de pasta media/
4. **Erro de CORS:** Verificar configurações CORS_ALLOWED_ORIGINS
5. **Erro de banco:** Verificar conexão e credenciais

### Logs Importantes
- **Django logs:** settings.LOGGING
- **Aplicação:** administration.models.SystemLog
- **Auditoria:** administration.models.AuditLog

## 📞 SUPORTE E CONTATO

### Informações do Projeto
- **Nome:** RH Acqua V2
- **Versão:** 2.0
- **Tecnologia:** Django 4.2.7
- **Licença:** Proprietária
- **Contato:** suporte@rhacqua.com.br

### Documentação Adicional
- **API Docs:** `/api/docs/`
- **Swagger:** `/api/swagger/`
- **ReDoc:** `/api/redoc/`

---

**Última atualização:** Dezembro 2024
**Versão da documentação:** 1.0 