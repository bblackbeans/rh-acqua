from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Report, ReportExecution, Dashboard, Widget, 
    Metric, MetricValue, ReportTemplate
)


class ReportExecutionInline(admin.TabularInline):
    model = ReportExecution
    extra = 0
    readonly_fields = ('executed_at', 'completed_at', 'status', 'executed_by')
    fields = ('executed_at', 'completed_at', 'status', 'executed_by', 'result_file')
    max_num = 5
    can_delete = False


class WidgetInline(admin.TabularInline):
    model = Widget
    extra = 1
    fields = ('title', 'widget_type', 'data_source', 'position_x', 'position_y', 'width', 'height')


class MetricValueInline(admin.TabularInline):
    model = MetricValue
    extra = 0
    readonly_fields = ('date', 'value')
    fields = ('date', 'value', 'context')
    max_num = 10
    can_delete = False


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'is_scheduled', 'last_run', 'next_run', 'created_at')
    list_filter = ('report_type', 'is_scheduled', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'last_run')
    filter_horizontal = ('recipients',)
    inlines = [ReportExecutionInline]
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'description', 'report_type', 'created_by')
        }),
        (_('Agendamento'), {
            'fields': ('is_scheduled', 'schedule_frequency', 'last_run', 'next_run', 'recipients')
        }),
        (_('Configurações'), {
            'fields': ('parameters', 'preferred_format')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ('report', 'executed_by', 'executed_at', 'completed_at', 'status')
    list_filter = ('status', 'executed_at')
    search_fields = ('report__name', 'executed_by__user__first_name', 'executed_by__user__last_name')
    readonly_fields = ('executed_at', 'report', 'executed_by')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('report', 'executed_by', 'executed_at', 'completed_at', 'status')
        }),
        (_('Resultado'), {
            'fields': ('result_file', 'error_message')
        }),
    )


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'owner__user__first_name', 'owner__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WidgetInline]
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'description', 'owner', 'is_public')
        }),
        (_('Layout'), {
            'fields': ('layout',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'widget_type', 'data_source')
    list_filter = ('widget_type', 'created_at')
    search_fields = ('title', 'dashboard__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('dashboard', 'title', 'widget_type', 'data_source')
        }),
        (_('Configurações'), {
            'fields': ('parameters',)
        }),
        (_('Posicionamento'), {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric_type', 'data_source', 'created_by', 'created_at')
    list_filter = ('metric_type', 'created_at')
    search_fields = ('name', 'description', 'data_source')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MetricValueInline]
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'description', 'metric_type', 'created_by')
        }),
        (_('Fonte de Dados'), {
            'fields': ('data_source', 'query', 'parameters')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    list_display = ('metric', 'date', 'value')
    list_filter = ('date', 'metric')
    search_fields = ('metric__name',)
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('metric', 'date', 'value')
        }),
        (_('Contexto'), {
            'fields': ('context',)
        }),
    )


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'description', 'report_type', 'created_by')
        }),
        (_('Template'), {
            'fields': ('template_file', 'html_template')
        }),
        (_('Configurações'), {
            'fields': ('parameters_schema',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.profile
        super().save_model(request, obj, form, change)
