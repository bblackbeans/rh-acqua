from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import (
    Hospital, Department, SystemConfiguration, 
    Notification, EmailTemplate, SystemLog, AuditLog
)
from users.models import UserProfile


class HospitalForm(forms.ModelForm):
    """
    Formulário para criação e edição de unidades hospitalares.
    """
    class Meta:
        model = Hospital
        fields = [
            'name', 'code', 'address', 'city', 'state', 'postal_code',
            'phone', 'email', 'website', 'description', 'is_active', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Hospital.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError(_('Já existe um hospital com este código.'))
        return code


class DepartmentForm(forms.ModelForm):
    """
    Formulário para criação e edição de departamentos.
    """
    class Meta:
        model = Department
        fields = [
            'name', 'code', 'hospital', 'description', 'manager', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas usuários ativos com perfil de gerente
        self.fields['manager'].queryset = UserProfile.objects.filter(
            user__is_active=True,
            role__in=['manager', 'admin']
        )
    
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        hospital = cleaned_data.get('hospital')
        
        if code and hospital:
            # Verifica se já existe um departamento com o mesmo código no mesmo hospital
            if Department.objects.filter(code=code, hospital=hospital).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                self.add_error('code', _('Já existe um departamento com este código neste hospital.'))
        
        return cleaned_data


class SystemConfigurationForm(forms.ModelForm):
    """
    Formulário para criação e edição de configurações do sistema.
    """
    class Meta:
        model = SystemConfiguration
        fields = [
            'key', 'value', 'value_type', 'description', 'category', 'is_public'
        ]
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'value_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_key(self):
        key = self.cleaned_data.get('key')
        if SystemConfiguration.objects.filter(key=key).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError(_('Já existe uma configuração com esta chave.'))
        return key
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.updated_by = self.user.profile
        if commit:
            instance.save()
        return instance


class NotificationForm(forms.ModelForm):
    """
    Formulário para criação de notificações.
    """
    recipients = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.filter(user__is_active=True),
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        label=_('Destinatários')
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'url',
            'related_object_type', 'related_object_id'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'related_object_type': forms.TextInput(attrs={'class': 'form-control'}),
            'related_object_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        # Não salva diretamente, pois precisamos criar múltiplas notificações
        if not commit:
            return super().save(commit=False)
        
        # Cria uma notificação para cada destinatário
        notifications = []
        for recipient in self.cleaned_data['recipients']:
            notification = Notification(
                recipient=recipient,
                title=self.cleaned_data['title'],
                message=self.cleaned_data['message'],
                notification_type=self.cleaned_data['notification_type'],
                url=self.cleaned_data['url'],
                related_object_type=self.cleaned_data['related_object_type'],
                related_object_id=self.cleaned_data['related_object_id']
            )
            notification.save()
            notifications.append(notification)
        
        return notifications


class EmailTemplateForm(forms.ModelForm):
    """
    Formulário para criação e edição de templates de e-mail.
    """
    class Meta:
        model = EmailTemplate
        fields = [
            'name', 'code', 'subject', 'body_html', 'body_text',
            'description', 'variables', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body_html': forms.Textarea(attrs={'class': 'form-control html-editor', 'rows': 10}),
            'body_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'variables': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if EmailTemplate.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise ValidationError(_('Já existe um template com este código.'))
        return code
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.updated_by = self.user.profile
        if commit:
            instance.save()
        return instance


class SystemLogFilterForm(forms.Form):
    """
    Formulário para filtrar logs do sistema.
    """
    level = forms.ChoiceField(
        choices=[('', '----------')] + list(SystemLog.LOG_LEVELS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Nível')
    )
    source = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Fonte')
    )
    user = forms.ModelChoiceField(
        queryset=UserProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Usuário')
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Data Inicial')
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Data Final')
    )
    message = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Mensagem')
    )


class AuditLogFilterForm(forms.Form):
    """
    Formulário para filtrar logs de auditoria.
    """
    action = forms.ChoiceField(
        choices=[('', '----------')] + list(AuditLog.ACTION_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Ação')
    )
    content_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Tipo de Conteúdo')
    )
    user = forms.ModelChoiceField(
        queryset=UserProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Usuário')
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Data Inicial')
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Data Final')
    )
    object_repr = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Representação do Objeto')
    )
