from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Hospital, Department, SystemConfiguration, SystemLog,
    AuditLog, Notification, EmailTemplate
)


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'state', 'is_active', 'created_at')
    list_filter = ('is_active', 'state', 'created_at')
    search_fields = ('name', 'code', 'city', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'code', 'description', 'is_active', 'logo')
        }),
        (_('Endereço'), {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        (_('Contato'), {
            'fields': ('phone', 'email', 'website')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1
    fields = ('name', 'code', 'manager', 'is_active')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'hospital', 'manager', 'is_active', 'created_at')
    list_filter = ('is_active', 'hospital', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('manager',)
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'code', 'hospital', 'description', 'is_active')
        }),
        (_('Gerenciamento'), {
            'fields': ('manager',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_type', 'category', 'is_public', 'updated_at')
    list_filter = ('value_type', 'category', 'is_public', 'updated_at')
    search_fields = ('key', 'value', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('key', 'value', 'value_type', 'description')
        }),
        (_('Categorização'), {
            'fields': ('category', 'is_public')
        }),
        (_('Informações Adicionais'), {
            'fields': ('updated_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'source', 'message', 'user', 'ip_address')
    list_filter = ('level', 'timestamp', 'source')
    search_fields = ('message', 'source', 'user__user__username', 'ip_address')
    readonly_fields = ('timestamp', 'level', 'message', 'source', 'user', 'ip_address',
                      'user_agent', 'request_path', 'request_method', 'additional_data')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('timestamp', 'level', 'message', 'source')
        }),
        (_('Usuário'), {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        (_('Requisição'), {
            'fields': ('request_path', 'request_method')
        }),
        (_('Dados Adicionais'), {
            'fields': ('additional_data',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'content_type', 'object_repr', 'ip_address')
    list_filter = ('action', 'timestamp', 'content_type')
    search_fields = ('user__user__username', 'object_repr', 'ip_address', 'content_type')
    readonly_fields = ('timestamp', 'user', 'action', 'content_type', 'object_id',
                      'object_repr', 'changes', 'ip_address', 'user_agent')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('timestamp', 'user', 'action')
        }),
        (_('Objeto'), {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        (_('Alterações'), {
            'fields': ('changes',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('ip_address', 'user_agent')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'created_at', 'read_at')
    list_filter = ('notification_type', 'created_at', 'read_at')
    search_fields = ('title', 'message', 'recipient__user__username')
    readonly_fields = ('created_at', 'read_at')
    raw_id_fields = ('recipient',)
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('recipient', 'title', 'message', 'notification_type')
        }),
        (_('Status'), {
            'fields': ('created_at', 'read_at')
        }),
        (_('Referências'), {
            'fields': ('url', 'related_object_type', 'related_object_id')
        }),
    )
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        for notification in queryset.filter(read_at__isnull=True):
            notification.mark_as_read()
        self.message_user(request, _('Notificações marcadas como lidas com sucesso.'))
    mark_as_read.short_description = _('Marcar como lidas')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('name', 'code', 'subject', 'body_html', 'body_text')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        (_('Conteúdo do E-mail'), {
            'fields': ('subject', 'body_html', 'body_text')
        }),
        (_('Variáveis'), {
            'fields': ('variables',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('updated_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.profile
        super().save_model(request, obj, form, change)
