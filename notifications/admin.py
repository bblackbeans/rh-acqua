from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    NotificationCategory, NotificationType, NotificationPreference,
    Notification, NotificationDelivery, Message, Announcement, AnnouncementDismissal
)


@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active', 'email_available', 'push_available', 'sms_available')
    list_filter = ('is_active', 'category', 'email_available', 'push_available', 'sms_available')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category', 'icon', 'color', 'is_active')
        }),
        (_('Canais Disponíveis'), {
            'fields': ('email_available', 'push_available', 'sms_available')
        }),
        (_('Templates de Mensagem'), {
            'fields': ('email_subject_template', 'email_body_template', 'push_title_template', 'push_body_template', 'sms_template')
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'email_enabled', 'push_enabled', 'sms_enabled', 'updated_at')
    list_filter = ('email_enabled', 'push_enabled', 'sms_enabled', 'notification_type')
    search_fields = ('user__username', 'user__email', 'notification_type__name')
    raw_id_fields = ('user', 'notification_type')
    date_hierarchy = 'updated_at'


class NotificationDeliveryInline(admin.TabularInline):
    model = NotificationDelivery
    extra = 0
    readonly_fields = ('channel', 'status', 'sent_at', 'delivered_at', 'error_message')
    can_delete = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'status', 'priority', 'created_at', 'read_at')
    list_filter = ('status', 'priority', 'notification_type', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    raw_id_fields = ('user', 'notification_type', 'content_type')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    date_hierarchy = 'created_at'
    inlines = [NotificationDeliveryInline]
    actions = ['mark_as_read', 'mark_as_unread', 'archive']
    
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, _('Notificações marcadas como lidas.'))
    mark_as_read.short_description = _('Marcar como lidas')
    
    def mark_as_unread(self, request, queryset):
        for notification in queryset:
            notification.mark_as_unread()
        self.message_user(request, _('Notificações marcadas como não lidas.'))
    mark_as_unread.short_description = _('Marcar como não lidas')
    
    def archive(self, request, queryset):
        for notification in queryset:
            notification.archive()
        self.message_user(request, _('Notificações arquivadas.'))
    archive.short_description = _('Arquivar')


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ('notification', 'channel', 'status', 'sent_at', 'delivered_at')
    list_filter = ('channel', 'status', 'sent_at', 'delivered_at')
    search_fields = ('notification__title', 'notification__user__username', 'notification__user__email')
    raw_id_fields = ('notification',)
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'delivered_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_sent', 'mark_as_delivered', 'mark_as_failed']
    
    def mark_as_sent(self, request, queryset):
        for delivery in queryset:
            delivery.mark_as_sent()
        self.message_user(request, _('Entregas marcadas como enviadas.'))
    mark_as_sent.short_description = _('Marcar como enviadas')
    
    def mark_as_delivered(self, request, queryset):
        for delivery in queryset:
            delivery.mark_as_delivered()
        self.message_user(request, _('Entregas marcadas como entregues.'))
    mark_as_delivered.short_description = _('Marcar como entregues')
    
    def mark_as_failed(self, request, queryset):
        for delivery in queryset:
            delivery.mark_as_failed(_('Marcado manualmente como falha.'))
        self.message_user(request, _('Entregas marcadas como falhas.'))
    mark_as_failed.short_description = _('Marcar como falhas')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'status', 'priority', 'created_at', 'read_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('subject', 'body', 'sender__username', 'sender__email', 'recipient__username', 'recipient__email')
    raw_id_fields = ('sender', 'recipient', 'parent', 'content_type')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread', 'archive']
    
    def mark_as_read(self, request, queryset):
        for message in queryset:
            message.mark_as_read()
        self.message_user(request, _('Mensagens marcadas como lidas.'))
    mark_as_read.short_description = _('Marcar como lidas')
    
    def mark_as_unread(self, request, queryset):
        for message in queryset:
            message.mark_as_unread()
        self.message_user(request, _('Mensagens marcadas como não lidas.'))
    mark_as_unread.short_description = _('Marcar como não lidas')
    
    def archive(self, request, queryset):
        for message in queryset:
            message.archive()
        self.message_user(request, _('Mensagens arquivadas.'))
    archive.short_description = _('Arquivar')


class AnnouncementDismissalInline(admin.TabularInline):
    model = AnnouncementDismissal
    extra = 0
    readonly_fields = ('user', 'dismissed_at')
    can_delete = False


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'publish_from', 'publish_until', 'created_at', 'created_by')
    list_filter = ('status', 'priority', 'show_on_dashboard', 'show_as_popup', 'dismissible')
    search_fields = ('title', 'content')
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    filter_horizontal = ('target_groups',)
    inlines = [AnnouncementDismissalInline]
    actions = ['publish', 'mark_as_draft', 'mark_as_expired']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'status', 'priority', 'url')
        }),
        (_('Período de Publicação'), {
            'fields': ('publish_from', 'publish_until')
        }),
        (_('Público-Alvo'), {
            'fields': ('target_all_users', 'target_groups', 'target_roles')
        }),
        (_('Opções de Exibição'), {
            'fields': ('show_on_dashboard', 'show_as_popup', 'dismissible')
        }),
        (_('Metadados'), {
            'fields': ('metadata', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def publish(self, request, queryset):
        for announcement in queryset:
            announcement.publish()
        self.message_user(request, _('Anúncios publicados.'))
    publish.short_description = _('Publicar')
    
    def mark_as_draft(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, _('Anúncios marcados como rascunho.'))
    mark_as_draft.short_description = _('Marcar como rascunho')
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, _('Anúncios marcados como expirados.'))
    mark_as_expired.short_description = _('Marcar como expirados')


@admin.register(AnnouncementDismissal)
class AnnouncementDismissalAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'dismissed_at')
    list_filter = ('dismissed_at',)
    search_fields = ('announcement__title', 'user__username', 'user__email')
    raw_id_fields = ('announcement', 'user')
    readonly_fields = ('dismissed_at',)
    date_hierarchy = 'dismissed_at'
