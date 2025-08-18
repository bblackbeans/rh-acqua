from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, CandidateProfile, RecruiterProfile, UserProfile, Education, Experience, TechnicalSkill, SoftSkill, Certification, Language

# Registros existentes...

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'get_role')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('user__role', 'user__is_active')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Nome Completo'
    
    def get_role(self, obj):
        return obj.user.get_role_display()
    get_role.short_description = 'Perfil'



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Configuração do admin para o modelo de usuário customizado."""
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'role', 'phone', 'date_of_birth', 'profile_picture', 'bio')}),
        (_('Informações de Candidato'), {'fields': ('cpf', 'address', 'city', 'state', 'zip_code'), 'classes': ('collapse',)}),
        (_('Informações de Recrutador'), {'fields': ('department', 'position', 'employee_id'), 'classes': ('collapse',)}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    """Configuração do admin para o perfil de candidato."""
    
    list_display = ('user', 'education_level', 'current_position', 'current_company', 'created_at')
    list_filter = ('education_level', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio', 'current_position')
    
    fieldsets = (
        (_('Usuário'), {'fields': ('user',)}),
        (_('Formação Acadêmica'), {'fields': ('education_level', 'institution', 'course', 'graduation_year')}),
        (_('Experiência Profissional'), {'fields': ('experience_years', 'current_position', 'current_company')}),
        (_('Perfil'), {'fields': ('bio', 'profile_picture')}),
        (_('Endereço'), {'fields': ('address', 'city', 'state', 'zip_code')}),
        (_('Contato'), {'fields': ('phone', 'whatsapp')}),
        (_('Identificação'), {'fields': ('cpf', 'rg', 'pis')}),
        (_('Configurações'), {'fields': ('is_public', 'share_data')}),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin para formação acadêmica."""
    list_display = ('user', 'curso', 'instituicao', 'nivel', 'inicio', 'fim', 'em_andamento')
    list_filter = ('nivel', 'em_andamento', 'created_at')
    search_fields = ('user__email', 'curso', 'instituicao')
    date_hierarchy = 'inicio'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin para experiência profissional."""
    list_display = ('user', 'cargo', 'empresa', 'inicio', 'fim', 'atual')
    list_filter = ('atual', 'created_at')
    search_fields = ('user__email', 'cargo', 'empresa')
    date_hierarchy = 'inicio'


@admin.register(TechnicalSkill)
class TechnicalSkillAdmin(admin.ModelAdmin):
    """Admin para habilidades técnicas."""
    list_display = ('user', 'nome', 'nivel')
    list_filter = ('nivel', 'created_at')
    search_fields = ('user__email', 'nome')


@admin.register(SoftSkill)
class SoftSkillAdmin(admin.ModelAdmin):
    """Admin para habilidades emocionais."""
    list_display = ('user', 'nome')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'nome')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin para certificações."""
    list_display = ('user', 'titulo', 'orgao', 'emissao', 'validade', 'sem_validade')
    list_filter = ('sem_validade', 'created_at')
    search_fields = ('user__email', 'titulo', 'orgao')
    date_hierarchy = 'emissao'


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin para idiomas."""
    list_display = ('user', 'idioma', 'idioma_outro', 'nivel')
    list_filter = ('idioma', 'nivel', 'created_at')
    search_fields = ('user__email', 'idioma', 'idioma_outro')


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    """Configuração do admin para o perfil de recrutador."""
    
    list_display = ('user', 'specialization', 'hiring_authority', 'vacancies_created', 'successful_hires')
    list_filter = ('hiring_authority', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'specialization')
    
    fieldsets = (
        (_('Usuário'), {'fields': ('user',)}),
        (_('Informações Profissionais'), {'fields': ('specialization', 'hiring_authority')}),
        (_('Estatísticas'), {'fields': ('vacancies_created', 'candidates_interviewed', 'successful_hires')}),
        (_('Preferências'), {'fields': ('notification_preferences',)}),
    )
