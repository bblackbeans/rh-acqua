from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Interview, InterviewFeedback, InterviewQuestion, 
    InterviewTemplate, TemplateQuestion, InterviewSchedule
)


class InterviewFeedbackInline(admin.StackedInline):
    model = InterviewFeedback
    can_delete = False
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class TemplateQuestionInline(admin.TabularInline):
    model = TemplateQuestion
    extra = 1
    ordering = ('order',)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'vacancy_title', 'type', 'status', 'scheduled_date', 'interviewer_name')
    list_filter = ('type', 'status', 'scheduled_date', 'interviewer')
    search_fields = ('application__candidate__user__first_name', 'application__candidate__user__last_name', 'application__vacancy__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'scheduled_date'
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('application', 'interviewer', 'type', 'status')
        }),
        (_('Agendamento'), {
            'fields': ('scheduled_date', 'duration', 'location', 'meeting_link')
        }),
        (_('Observações'), {
            'fields': ('notes',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [InterviewFeedbackInline]
    
    def candidate_name(self, obj):
        return obj.application.candidate.user.get_full_name()
    candidate_name.short_description = _('Candidato')
    
    def vacancy_title(self, obj):
        return obj.application.vacancy.title
    vacancy_title.short_description = _('Vaga')
    
    def interviewer_name(self, obj):
        return obj.interviewer.user.get_full_name()
    interviewer_name.short_description = _('Entrevistador')


@admin.register(InterviewFeedback)
class InterviewFeedbackAdmin(admin.ModelAdmin):
    list_display = ('interview', 'technical_score', 'communication_score', 'cultural_fit_score', 'total_score', 'recommendation')
    list_filter = ('recommendation', 'created_at')
    search_fields = ('interview__application__candidate__user__first_name', 'interview__application__candidate__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = _('Pontuação Total')


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'category', 'is_active', 'created_by')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('text',)
    readonly_fields = ('created_at', 'updated_at')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = _('Pergunta')


@admin.register(InterviewTemplate)
class InterviewTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count', 'is_active', 'created_by')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TemplateQuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = _('Número de Perguntas')


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ('interviewer_name', 'date', 'start_time', 'end_time', 'is_recurring', 'recurrence_pattern')
    list_filter = ('is_recurring', 'recurrence_pattern', 'date')
    search_fields = ('interviewer__user__first_name', 'interviewer__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    def interviewer_name(self, obj):
        return obj.interviewer.user.get_full_name()
    interviewer_name.short_description = _('Entrevistador')
