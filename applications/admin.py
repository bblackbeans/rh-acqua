from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Application, ApplicationEvaluation, Resume, Education, WorkExperience, ApplicationComplementaryInfo, ApplicationFavorite


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1


class ApplicationEvaluationInline(admin.TabularInline):
    model = ApplicationEvaluation
    extra = 0
    readonly_fields = ('evaluator', 'technical_score', 'experience_score', 'cultural_fit_score', 'comments', 'created_at')
    can_delete = False
    max_num = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'vacancy_title', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'vacancy__hospital', 'vacancy__department')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'vacancy__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('candidate', 'vacancy', 'status')
        }),
        (_('Detalhes da Candidatura'), {
            'fields': ('cover_letter', 'resume')
        }),
        (_('Informações Adicionais'), {
            'fields': ('recruiter_notes', 'created_at', 'updated_at')
        }),
    )
    inlines = [ApplicationEvaluationInline]
    
    def candidate_name(self, obj):
        return obj.candidate.user.get_full_name()
    candidate_name.short_description = _('Candidato')
    
    def vacancy_title(self, obj):
        return obj.vacancy.title
    vacancy_title.short_description = _('Vaga')


@admin.register(ApplicationEvaluation)
class ApplicationEvaluationAdmin(admin.ModelAdmin):
    list_display = ('application', 'evaluator_name', 'technical_score', 'experience_score', 'cultural_fit_score', 'total_score', 'created_at')
    list_filter = ('created_at', 'evaluator')
    search_fields = ('application__candidate__user__first_name', 'application__candidate__user__last_name', 'evaluator__user__first_name', 'evaluator__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def evaluator_name(self, obj):
        return obj.evaluator.user.get_full_name()
    evaluator_name.short_description = _('Avaliador')
    
    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = _('Pontuação Total')


@admin.register(ApplicationFavorite)
class ApplicationFavoriteAdmin(admin.ModelAdmin):
    list_display = ['application', 'recruiter', 'created_at']
    list_filter = ['created_at']
    search_fields = ['application__candidate__user__first_name', 'recruiter__user__first_name']
    readonly_fields = ['created_at']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'created_at', 'updated_at')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('candidate', 'summary')
        }),
        (_('Habilidades e Qualificações'), {
            'fields': ('skills', 'languages', 'certifications')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [EducationInline, WorkExperienceInline]
    
    def candidate_name(self, obj):
        return obj.candidate.user.get_full_name()
    candidate_name.short_description = _('Candidato')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('resume', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current')
    list_filter = ('degree', 'is_current')
    search_fields = ('institution', 'field_of_study', 'resume__candidate__user__first_name', 'resume__candidate__user__last_name')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('resume', 'company', 'position', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('company', 'position', 'resume__candidate__user__first_name', 'resume__candidate__user__last_name')


@admin.register(ApplicationComplementaryInfo)
class ApplicationComplementaryInfoAdmin(admin.ModelAdmin):
    list_display = ('application', 'trabalha_atualmente', 'experiencia_area', 'inicio_imediato', 'trabalhou_acqua', 'parentes_instituicao')
    list_filter = ('trabalha_atualmente', 'experiencia_area', 'inicio_imediato', 'trabalhou_acqua', 'parentes_instituicao')
    search_fields = ('application__candidate__user__first_name', 'application__candidate__user__last_name', 'application__vacancy__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Candidatura'), {
            'fields': ('application',)
        }),
        (_('Histórico Profissional'), {
            'fields': ('trabalha_atualmente', 'funcao_atual', 'experiencia_area', 'descricao_experiencia', 'ultima_funcao', 'tempo_experiencia')
        }),
        (_('Disponibilidade'), {
            'fields': ('disponibilidade_manha', 'disponibilidade_tarde', 'disponibilidade_noite', 'disponibilidade_comercial', 'disponibilidade_plantao_dia', 'disponibilidade_plantao_noite', 'inicio_imediato')
        }),
        (_('Informações ACQUA'), {
            'fields': ('trabalhou_acqua', 'area_cargo_acqua', 'data_desligamento')
        }),
        (_('Parentes na Instituição'), {
            'fields': ('parentes_instituicao', 'grau_parentesco', 'nome_parente_setor')
        }),
        (_('Declarações'), {
            'fields': ('declaracao_veracidade', 'declaracao_edital', 'autorizacao_dados', 'data_declaracao')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
