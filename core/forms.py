from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import (
    Tag, Category, Attachment, Comment, Dashboard, Widget,
    MenuItem, FAQ, Feedback, Announcement
)
from users.models import UserProfile


class TagForm(forms.ModelForm):
    """
    Formulário para criação e edição de tags.
    """
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            name = self.cleaned_data.get('name')
            if name:
                slug = slugify(name)
        
        # Verifica se já existe uma tag com este slug
        if Tag.objects.filter(slug=slug).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError(_('Já existe uma tag com este slug.'))
        
        return slug


class CategoryForm(forms.ModelForm):
    """
    Formulário para criação e edição de categorias.
    """
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclui a própria categoria e suas filhas das opções de categoria pai
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(
                pk__in=[self.instance.pk] + list(Category.objects.filter(parent=self.instance).values_list('pk', flat=True))
            )
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            name = self.cleaned_data.get('name')
            if name:
                slug = slugify(name)
        
        # Verifica se já existe uma categoria com este slug
        if Category.objects.filter(slug=slug).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError(_('Já existe uma categoria com este slug.'))
        
        return slug


class AttachmentForm(forms.ModelForm):
    """
    Formulário para upload de anexos.
    """
    class Meta:
        model = Attachment
        fields = ['file', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o usuário que fez o upload
        if self.user and hasattr(self.user, 'profile'):
            instance.uploaded_by = self.user.profile
        
        # Define o tipo de conteúdo e tamanho do arquivo
        if instance.file:
            instance.content_type = instance.file.content_type
            instance.size = instance.file.size
        
        if commit:
            instance.save()
        
        return instance


class CommentForm(forms.ModelForm):
    """
    Formulário para criação de comentários.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.content_type = kwargs.pop('content_type', None)
        self.object_id = kwargs.pop('object_id', None)
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o autor do comentário
        if self.user and hasattr(self.user, 'profile'):
            instance.author = self.user.profile
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        # Define o tipo de conteúdo e ID do objeto
        if self.content_type:
            instance.content_type = self.content_type
        
        if self.object_id:
            instance.object_id = self.object_id
        
        # Define o comentário pai, se houver
        if self.parent:
            instance.parent = self.parent
        
        if commit:
            instance.save()
        
        return instance


class DashboardForm(forms.ModelForm):
    """
    Formulário para criação e edição de dashboards.
    """
    class Meta:
        model = Dashboard
        fields = ['title', 'description', 'is_default', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o proprietário do dashboard
        if self.user and hasattr(self.user, 'profile'):
            instance.owner = self.user.profile
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        # Inicializa o layout, se for um novo dashboard
        if not instance.pk and not instance.layout:
            instance.layout = {
                'version': 1,
                'columns': 12,
                'rows': 12,
                'widgets': []
            }
        
        if commit:
            instance.save()
        
        return instance


class WidgetForm(forms.ModelForm):
    """
    Formulário para criação e edição de widgets.
    """
    class Meta:
        model = Widget
        fields = [
            'title', 'widget_type', 'data_source', 'configuration',
            'position_x', 'position_y', 'width', 'height'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'widget_type': forms.Select(attrs={'class': 'form-control'}),
            'data_source': forms.TextInput(attrs={'class': 'form-control'}),
            'configuration': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
            'position_x': forms.NumberInput(attrs={'class': 'form-control'}),
            'position_y': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.dashboard = kwargs.pop('dashboard', None)
        super().__init__(*args, **kwargs)
        
        if self.dashboard:
            self.fields['dashboard'] = forms.ModelChoiceField(
                queryset=Dashboard.objects.filter(pk=self.dashboard.pk),
                initial=self.dashboard,
                widget=forms.HiddenInput()
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o dashboard do widget
        if self.dashboard:
            instance.dashboard = self.dashboard
        
        # Define o usuário que criou/atualizou o widget
        if self.user and hasattr(self.user, 'profile'):
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        if commit:
            instance.save()
        
        return instance


class MenuItemForm(forms.ModelForm):
    """
    Formulário para criação e edição de itens de menu.
    """
    class Meta:
        model = MenuItem
        fields = [
            'title', 'url', 'icon', 'parent', 'order',
            'is_active', 'required_permissions', 'required_roles'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'required_permissions': forms.TextInput(attrs={'class': 'form-control'}),
            'required_roles': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclui o próprio item e seus filhos das opções de item pai
        if self.instance.pk:
            self.fields['parent'].queryset = MenuItem.objects.exclude(
                pk__in=[self.instance.pk] + list(MenuItem.objects.filter(parent=self.instance).values_list('pk', flat=True))
            )


class FAQForm(forms.ModelForm):
    """
    Formulário para criação e edição de FAQs.
    """
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'tags', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control rich-text-editor', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o usuário que criou/atualizou a FAQ
        if self.user and hasattr(self.user, 'profile'):
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class FeedbackForm(forms.ModelForm):
    """
    Formulário para envio de feedback.
    """
    class Meta:
        model = Feedback
        fields = ['title', 'description', 'feedback_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o usuário que enviou o feedback
        if self.user and hasattr(self.user, 'profile'):
            instance.user = self.user.profile
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        if commit:
            instance.save()
        
        return instance


class FeedbackResponseForm(forms.ModelForm):
    """
    Formulário para resposta a um feedback.
    """
    class Meta:
        model = Feedback
        fields = ['status', 'priority', 'assigned_to', 'resolution']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'resolution': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas usuários ativos com perfil de administrador ou gerente
        self.fields['assigned_to'].queryset = UserProfile.objects.filter(
            user__is_active=True,
            role__in=['admin', 'manager']
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o usuário que atualizou o feedback
        if self.user and hasattr(self.user, 'profile'):
            instance.updated_by = self.user.profile
        
        # Se o status for alterado para 'resolvido', define a data de resolução
        if instance.status == 'resolved' and not instance.resolved_at:
            instance.resolved_at = timezone.now()
        
        if commit:
            instance.save()
        
        return instance


class AnnouncementForm(forms.ModelForm):
    """
    Formulário para criação e edição de anúncios.
    """
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'start_date', 'end_date',
            'is_active', 'target_roles', 'is_important'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control rich-text-editor', 'rows': 5}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_roles': forms.TextInput(attrs={'class': 'form-control'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            self.add_error('end_date', _('A data de término deve ser posterior à data de início.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Define o usuário que criou/atualizou o anúncio
        if self.user and hasattr(self.user, 'profile'):
            instance.created_by = self.user.profile
            instance.updated_by = self.user.profile
        
        if commit:
            instance.save()
        
        return instance
