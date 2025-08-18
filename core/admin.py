from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Tag, Category, Attachment, Comment, Dashboard, Widget,
    MenuItem, FAQ, Feedback, Announcement
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'icon')
    search_fields = ('name', 'slug', 'description')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'size', 'uploaded_by', 'uploaded_at')
    search_fields = ('name', 'description', 'content_type')
    list_filter = ('content_type', 'uploaded_at')
    readonly_fields = ('size', 'uploaded_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_type', 'object_id', 'created_at', 'is_active')
    search_fields = ('content', 'author__user__username', 'content_type', 'object_id')
    list_filter = ('is_active', 'created_at', 'content_type')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_default', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'owner__user__username')
    list_filter = ('is_default', 'is_public', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


class WidgetInline(admin.TabularInline):
    model = Widget
    extra = 1
    fields = ('title', 'widget_type', 'data_source', 'position_x', 'position_y', 'width', 'height')


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'dashboard', 'position_x', 'position_y', 'width', 'height')
    search_fields = ('title', 'data_source', 'dashboard__title')
    list_filter = ('widget_type', 'dashboard')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'parent', 'order', 'is_active')
    search_fields = ('title', 'url')
    list_filter = ('is_active', 'parent')
    list_editable = ('order', 'is_active')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_filter = ('is_active', 'category', 'created_at')
    list_editable = ('order', 'is_active')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'feedback_type', 'priority', 'status', 'user', 'created_at')
    search_fields = ('title', 'description', 'user__user__username')
    list_filter = ('feedback_type', 'priority', 'status', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('title', 'description', 'feedback_type', 'priority', 'status')
        }),
        (_('Usuário'), {
            'fields': ('user', 'assigned_to')
        }),
        (_('Resolução'), {
            'fields': ('resolution', 'resolved_at')
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'is_important')
    search_fields = ('title', 'content')
    list_filter = ('is_active', 'is_important', 'start_date', 'end_date')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('title', 'content', 'is_active', 'is_important')
        }),
        (_('Período'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Público Alvo'), {
            'fields': ('target_roles',)
        }),
        (_('Informações Adicionais'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')
        }),
    )
