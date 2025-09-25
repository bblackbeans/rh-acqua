from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Vacancy, Hospital, Department, JobCategory, Skill, VacancyAttachment


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'created_at']
    list_filter = ['state', 'city']
    search_fields = ['name', 'city', 'state']
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'manager', 'created_at']
    list_filter = ['hospital']
    search_fields = ['name', 'hospital__name']
    ordering = ['hospital__name', 'name']
    autocomplete_fields = ['hospital', 'manager']


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']
    list_editable = ['is_active']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['name']
    autocomplete_fields = ['category']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    exclude = ("slug", "views_count", "applications_count")
    list_display = [
        'title', 'hospital', 'department', 'status', 'contract_type', 
        'experience_level', 'recruiter', 'created_at'
    ]
    list_filter = [
        'status', 'contract_type', 'experience_level', 'hospital', 
        'department', 'is_remote', 'created_at'
    ]
    search_fields = ['title', 'description', 'requirements', 'hospital__name', 'department__name']
    ordering = ['-created_at']
    list_editable = ['status']
    autocomplete_fields = ['hospital', 'department', 'category', 'skills', 'recruiter']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('title', 'description', 'requirements', 'benefits')
        }),
        (_('Localização e Organização'), {
            'fields': ('hospital', 'department', 'category', 'location', 'is_remote')
        }),
        (_('Detalhes da Vaga'), {
            'fields': ('status', 'contract_type', 'experience_level', 'skills')
        }),
        (_('Responsável'), {
            'fields': ('recruiter',)
        }),
        (_('Remuneração'), {
            'fields': ('salary_range_min', 'salary_range_max', 'is_salary_visible', 'monthly_hours')
        }),
        (_('Datas'), {
            'fields': ('publication_date', 'closing_date')
        }),
        (_('Sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Define automaticamente o recruiter ao criar uma nova vaga.
        Permite que administradores editem o recruiter.
        """
        # Se é uma nova vaga (não está sendo editada)
        if not change:
            if hasattr(request.user, "recruiter"):
                obj.recruiter = request.user.recruiter
            else:
                obj.recruiter = request.user
        # Se é uma edição e o usuário é administrador, permite editar o recruiter
        elif request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            # O recruiter já foi definido pelo formulário, não precisa fazer nada
            pass
        # Se não é admin, mantém o recruiter original
        else:
            # Mantém o recruiter original da vaga
            if obj.pk:
                original_obj = Vacancy.objects.get(pk=obj.pk)
                obj.recruiter = original_obj.recruiter
        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza o formulário baseado no usuário.
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Se não é administrador, torna o campo recruiter somente leitura
        if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')):
            if 'recruiter' in form.base_fields:
                form.base_fields['recruiter'].disabled = True
                form.base_fields['recruiter'].help_text = "Apenas administradores podem alterar o recrutador responsável."
        
        return form
    
    def get_queryset(self, request):
        """
        Filtra as vagas baseado no usuário logado.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'role') and request.user.role == 'admin':
            return qs
        else:
            return qs.filter(recruiter=request.user)


@admin.register(VacancyAttachment)
class VacancyAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'vacancy', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'vacancy__title']
    ordering = ['-uploaded_at']
    autocomplete_fields = ['vacancy']
