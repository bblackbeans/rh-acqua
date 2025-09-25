"""
Interface administrativa para o sistema de email
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SMTPConfiguration, 
    EmailTemplate, 
    EmailTrigger, 
    EmailQueue, 
    EmailLog
)


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'port', 'from_email', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_active', 'is_default', 'use_tls', 'use_ssl', 'created_at']
    search_fields = ['name', 'host', 'from_email', 'from_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'is_active', 'is_default')
        }),
        ('Configurações do Servidor', {
            'fields': ('host', 'port', 'use_tls', 'use_ssl')
        }),
        ('Autenticação', {
            'fields': ('username', 'password')
        }),
        ('Remetente', {
            'fields': ('from_email', 'from_name')
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['trigger_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'html_content']
    readonly_fields = ['created_at', 'updated_at', 'variables_preview']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'trigger_type', 'is_active')
        }),
        ('Conteúdo do Email', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Variáveis', {
            'fields': ('variables', 'variables_preview'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def variables_preview(self, obj):
        """Mostra uma prévia das variáveis disponíveis"""
        if obj.variables:
            variables_list = []
            for key, description in obj.variables.items():
                variables_list.append(f"<strong>{key}</strong>: {description}")
            return mark_safe("<br>".join(variables_list))
        return "Nenhuma variável definida"
    variables_preview.short_description = "Variáveis Disponíveis"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailTrigger)
class EmailTriggerAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'template', 'smtp_config', 'is_active', 'priority', 'delay_minutes']
    list_filter = ['trigger_type', 'is_active', 'priority', 'created_at']
    search_fields = ['name', 'template__name', 'smtp_config__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'trigger_type', 'is_active')
        }),
        ('Configurações', {
            'fields': ('template', 'smtp_config', 'priority', 'delay_minutes')
        }),
        ('Condições', {
            'fields': ('conditions',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = [
        'to_email', 'subject_preview', 'trigger', 'status', 'priority', 
        'scheduled_at', 'sent_at', 'retry_count'
    ]
    list_filter = ['status', 'priority', 'trigger__trigger_type', 'scheduled_at', 'sent_at']
    search_fields = ['to_email', 'to_name', 'subject', 'trigger__name']
    readonly_fields = [
        'created_at', 'updated_at', 'sent_at', 'retry_count', 
        'html_content_preview', 'context_data_preview'
    ]
    
    fieldsets = (
        ('Informações do Email', {
            'fields': ('trigger', 'to_email', 'to_name', 'subject')
        }),
        ('Conteúdo', {
            'fields': ('html_content', 'text_content', 'html_content_preview'),
            'classes': ('collapse',)
        }),
        ('Status e Agendamento', {
            'fields': ('status', 'priority', 'scheduled_at', 'sent_at', 'retry_count', 'max_retries')
        }),
        ('Erro', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Dados de Contexto', {
            'fields': ('context_data', 'context_data_preview'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_preview(self, obj):
        """Mostra uma prévia do assunto"""
        if len(obj.subject) > 50:
            return obj.subject[:50] + "..."
        return obj.subject
    subject_preview.short_description = "Assunto"
    
    def html_content_preview(self, obj):
        """Mostra uma prévia do conteúdo HTML"""
        if obj.html_content:
            preview = obj.html_content[:200] + "..." if len(obj.html_content) > 200 else obj.html_content
            return mark_safe(f"<div style='max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;'>{preview}</div>")
        return "Sem conteúdo HTML"
    html_content_preview.short_description = "Prévia do Conteúdo HTML"
    
    def context_data_preview(self, obj):
        """Mostra uma prévia dos dados de contexto"""
        if obj.context_data:
            import json
            formatted_data = json.dumps(obj.context_data, indent=2, ensure_ascii=False)
            return mark_safe(f"<pre style='max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;'>{formatted_data}</pre>")
        return "Sem dados de contexto"
    context_data_preview.short_description = "Dados de Contexto"
    
    actions = ['retry_failed_emails', 'cancel_pending_emails']
    
    def retry_failed_emails(self, request, queryset):
        """Ação para tentar reenviar emails que falharam"""
        from .services import EmailQueueService
        
        retried_count = 0
        for email_queue in queryset.filter(status='failed'):
            if email_queue.can_retry():
                email_queue.status = 'pending'
                email_queue.scheduled_at = timezone.now()
                email_queue.save()
                retried_count += 1
        
        self.message_user(request, f"{retried_count} emails foram marcados para reenvio.")
    retry_failed_emails.short_description = "Tentar reenviar emails falhados"
    
    def cancel_pending_emails(self, request, queryset):
        """Ação para cancelar emails pendentes"""
        cancelled_count = queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, f"{cancelled_count} emails foram cancelados.")
    cancel_pending_emails.short_description = "Cancelar emails pendentes"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'to_email', 'subject_preview', 'trigger', 'status', 
        'sent_at', 'retry_count', 'processing_time', 'created_at'
    ]
    list_filter = ['status', 'trigger__trigger_type', 'sent_at', 'created_at']
    search_fields = ['to_email', 'to_name', 'subject', 'trigger__name']
    readonly_fields = [
        'email_queue', 'trigger', 'smtp_config', 'to_email', 'to_name', 
        'subject', 'status', 'sent_at', 'error_message', 'retry_count', 
        'processing_time', 'created_at'
    ]
    
    fieldsets = (
        ('Informações do Email', {
            'fields': ('email_queue', 'trigger', 'smtp_config')
        }),
        ('Destinatário', {
            'fields': ('to_email', 'to_name')
        }),
        ('Conteúdo', {
            'fields': ('subject',)
        }),
        ('Status e Resultado', {
            'fields': ('status', 'sent_at', 'retry_count', 'processing_time')
        }),
        ('Erro', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def subject_preview(self, obj):
        """Mostra uma prévia do assunto"""
        if len(obj.subject) > 50:
            return obj.subject[:50] + "..."
        return obj.subject
    subject_preview.short_description = "Assunto"
    
    def has_add_permission(self, request):
        """Logs não podem ser criados manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs não podem ser editados"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Logs podem ser deletados apenas por superusuários"""
        return request.user.is_superuser


# Personalizar o título do admin
admin.site.site_header = "Sistema de Email - RH Acqua"
admin.site.site_title = "Email System"
admin.site.index_title = "Gerenciamento de Emails"

# Adicionar links customizados ao admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib.admin import AdminSite

class EmailSystemAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('email-system/', self.admin_view(self.email_system_dashboard), name='email_system_dashboard'),
            path('email-system/queue/', self.admin_view(self.email_system_queue), name='email_system_queue'),
            path('email-system/logs/', self.admin_view(self.email_system_logs), name='email_system_logs'),
            path('email-system/api/test-email/', self.admin_view(self.email_system_test_email), name='email_system_test_email'),
            path('email-system/api/stats/', self.admin_view(self.email_system_stats), name='email_system_stats'),
        ]
        return custom_urls + urls
    
    def email_system_dashboard(self, request):
        from .admin_views import email_dashboard_admin
        return email_dashboard_admin(request)
    
    def email_system_queue(self, request):
        from .admin_views import email_queue_admin
        return email_queue_admin(request)
    
    def email_system_logs(self, request):
        from .admin_views import email_logs_admin
        return email_logs_admin(request)
    
    def email_system_test_email(self, request):
        from .admin_views import TestEmailAdminView
        view = TestEmailAdminView()
        return view.post(request)
    
    def email_system_stats(self, request):
        from .admin_views import email_stats_api_admin
        return email_stats_api_admin(request)
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['email_system_links'] = [
            {
                'name': 'Dashboard do Sistema de Email',
                'url': reverse('admin:email_system_dashboard'),
                'description': 'Visão geral e estatísticas do sistema de email'
            },
            {
                'name': 'Fila de Emails',
                'url': reverse('admin:email_system_queue'),
                'description': 'Gerenciar emails pendentes e com falha'
            },
            {
                'name': 'Logs de Email',
                'url': reverse('admin:email_system_logs'),
                'description': 'Histórico completo de envios de email'
            },
        ]
        return super().index(request, extra_context)

# Substituir o admin site padrão
admin.site.__class__ = EmailSystemAdminSite