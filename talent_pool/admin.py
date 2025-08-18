from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    TalentPool, Talent, TalentSkill, Tag, TalentTag, 
    TalentNote, SavedSearch, TalentRecommendation
)


class TalentSkillInline(admin.TabularInline):
    model = TalentSkill
    extra = 1


class TalentTagInline(admin.TabularInline):
    model = TalentTag
    extra = 1


class TalentNoteInline(admin.StackedInline):
    model = TalentNote
    extra = 0
    readonly_fields = ('author', 'created_at', 'updated_at')


@admin.register(TalentPool)
class TalentPoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'talent_count', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def talent_count(self, obj):
        return obj.talents.count()
    talent_count.short_description = _('Número de Talentos')


@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'status', 'source', 'last_contact_date', 'created_at')
    list_filter = ('status', 'source', 'pools', 'departments_of_interest')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'candidate__user__email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('pools', 'departments_of_interest')
    inlines = [TalentSkillInline, TalentTagInline, TalentNoteInline]
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('candidate', 'status', 'source')
        }),
        (_('Categorização'), {
            'fields': ('pools', 'departments_of_interest')
        }),
        (_('Informações Salariais'), {
            'fields': ('salary_expectation_min', 'salary_expectation_max')
        }),
        (_('Datas'), {
            'fields': ('available_start_date', 'last_contact_date', 'created_at', 'updated_at')
        }),
        (_('Observações'), {
            'fields': ('notes',)
        }),
    )
    
    def full_name(self, obj):
        return obj.candidate.user.get_full_name()
    full_name.short_description = _('Nome Completo')
    
    def email(self, obj):
        return obj.candidate.user.email
    email.short_description = _('E-mail')


@admin.register(TalentSkill)
class TalentSkillAdmin(admin.ModelAdmin):
    list_display = ('talent_name', 'skill_name', 'proficiency', 'years_experience', 'is_primary')
    list_filter = ('proficiency', 'is_primary', 'skill')
    search_fields = ('talent__candidate__user__first_name', 'talent__candidate__user__last_name', 'skill__name')
    
    def talent_name(self, obj):
        return obj.talent.candidate.user.get_full_name()
    talent_name.short_description = _('Talento')
    
    def skill_name(self, obj):
        return obj.skill.name
    skill_name.short_description = _('Habilidade')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(TalentTag)
class TalentTagAdmin(admin.ModelAdmin):
    list_display = ('talent_name', 'tag_name', 'added_by', 'added_at')
    list_filter = ('tag', 'added_at')
    search_fields = ('talent__candidate__user__first_name', 'talent__candidate__user__last_name', 'tag__name')
    readonly_fields = ('added_at',)
    
    def talent_name(self, obj):
        return obj.talent.candidate.user.get_full_name()
    talent_name.short_description = _('Talento')
    
    def tag_name(self, obj):
        return obj.tag.name
    tag_name.short_description = _('Tag')


@admin.register(TalentNote)
class TalentNoteAdmin(admin.ModelAdmin):
    list_display = ('talent_name', 'author_name', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('talent__candidate__user__first_name', 'talent__candidate__user__last_name', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    def talent_name(self, obj):
        return obj.talent.candidate.user.get_full_name()
    talent_name.short_description = _('Talento')
    
    def author_name(self, obj):
        if obj.author:
            return obj.author.user.get_full_name()
        return _('Desconhecido')
    author_name.short_description = _('Autor')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Conteúdo')


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'owner__user__first_name', 'owner__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def owner_name(self, obj):
        return obj.owner.user.get_full_name()
    owner_name.short_description = _('Proprietário')


@admin.register(TalentRecommendation)
class TalentRecommendationAdmin(admin.ModelAdmin):
    list_display = ('talent_name', 'vacancy_title', 'status', 'match_score', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('talent__candidate__user__first_name', 'talent__candidate__user__last_name', 'vacancy__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def talent_name(self, obj):
        return obj.talent.candidate.user.get_full_name()
    talent_name.short_description = _('Talento')
    
    def vacancy_title(self, obj):
        return obj.vacancy.title
    vacancy_title.short_description = _('Vaga')
