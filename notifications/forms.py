from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import (
    NotificationCategory, NotificationType, NotificationPreference,
    Notification, Message, Announcement
)

User = get_user_model()


class NotificationCategoryForm(forms.ModelForm):
    """
    Formulário para categoria de notificação.
    """
    class Meta:
        model = NotificationCategory
        fields = ['name', 'slug', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class NotificationTypeForm(forms.ModelForm):
    """
    Formulário para tipo de notificação.
    """
    class Meta:
        model = NotificationType
        fields = [
            'name', 'slug', 'description', 'category', 'icon', 'color', 'is_active',
            'email_available', 'push_available', 'sms_available',
            'email_subject_template', 'email_body_template',
            'push_title_template', 'push_body_template',
            'sms_template'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'email_body_template': forms.Textarea(attrs={'rows': 5}),
            'push_body_template': forms.Textarea(attrs={'rows': 3}),
            'sms_template': forms.Textarea(attrs={'rows': 3}),
        }


class NotificationPreferenceForm(forms.ModelForm):
    """
    Formulário para preferência de notificação.
    """
    class Meta:
        model = NotificationPreference
        fields = ['notification_type', 'email_enabled', 'push_enabled', 'sms_enabled']


class NotificationPreferenceBulkForm(forms.Form):
    """
    Formulário para atualização em massa de preferências de notificação.
    """
    notification_types = forms.ModelMultipleChoiceField(
        queryset=NotificationType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Tipos de Notificação')
    )
    email_enabled = forms.BooleanField(
        required=False,
        label=_('E-mail Habilitado')
    )
    push_enabled = forms.BooleanField(
        required=False,
        label=_('Push Habilitado')
    )
    sms_enabled = forms.BooleanField(
        required=False,
        label=_('SMS Habilitado')
    )


class NotificationForm(forms.ModelForm):
    """
    Formulário para notificação.
    """
    class Meta:
        model = Notification
        fields = ['user', 'notification_type', 'title', 'message', 'priority', 'url']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }


class NotificationBulkForm(forms.Form):
    """
    Formulário para criação em massa de notificações.
    """
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple,
        required=True,
        label=_('Usuários')
    )
    notification_type = forms.ModelChoiceField(
        queryset=NotificationType.objects.filter(is_active=True),
        required=True,
        label=_('Tipo de Notificação')
    )
    title = forms.CharField(
        max_length=255,
        required=True,
        label=_('Título')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=True,
        label=_('Mensagem')
    )
    priority = forms.ChoiceField(
        choices=Notification.PRIORITY_CHOICES,
        required=True,
        initial='normal',
        label=_('Prioridade')
    )
    url = forms.CharField(
        max_length=255,
        required=False,
        label=_('URL')
    )


class MessageForm(forms.ModelForm):
    """
    Formulário para mensagem.
    """
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body', 'priority']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5}),
        }


class MessageReplyForm(forms.ModelForm):
    """
    Formulário para resposta de mensagem.
    """
    class Meta:
        model = Message
        fields = ['body', 'priority']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5}),
        }


class MessageBulkForm(forms.Form):
    """
    Formulário para criação em massa de mensagens.
    """
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple,
        required=True,
        label=_('Destinatários')
    )
    subject = forms.CharField(
        max_length=255,
        required=True,
        label=_('Assunto')
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=True,
        label=_('Corpo')
    )
    priority = forms.ChoiceField(
        choices=Message.PRIORITY_CHOICES,
        required=True,
        initial='normal',
        label=_('Prioridade')
    )


class AnnouncementForm(forms.ModelForm):
    """
    Formulário para anúncio.
    """
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'status', 'priority',
            'publish_from', 'publish_until',
            'target_all_users', 'target_groups', 'target_roles',
            'show_on_dashboard', 'show_as_popup', 'dismissible',
            'url'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'publish_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'publish_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'target_roles': forms.JSONInput(),
        }


class NotificationFilterForm(forms.Form):
    """
    Formulário para filtrar notificações.
    """
    status = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Notification.STATUS_CHOICES),
        required=False,
        label=_('Status')
    )
    priority = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Notification.PRIORITY_CHOICES),
        required=False,
        label=_('Prioridade')
    )
    notification_type = forms.ModelChoiceField(
        queryset=NotificationType.objects.filter(is_active=True),
        required=False,
        label=_('Tipo de Notificação')
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Inicial')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Final')
    )
    search = forms.CharField(
        required=False,
        label=_('Pesquisar')
    )


class MessageFilterForm(forms.Form):
    """
    Formulário para filtrar mensagens.
    """
    status = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Message.STATUS_CHOICES),
        required=False,
        label=_('Status')
    )
    priority = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Message.PRIORITY_CHOICES),
        required=False,
        label=_('Prioridade')
    )
    sender = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        label=_('Remetente')
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Inicial')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Final')
    )
    search = forms.CharField(
        required=False,
        label=_('Pesquisar')
    )


class AnnouncementFilterForm(forms.Form):
    """
    Formulário para filtrar anúncios.
    """
    status = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Announcement.STATUS_CHOICES),
        required=False,
        label=_('Status')
    )
    priority = forms.ChoiceField(
        choices=[('', _('Todos'))] + list(Announcement.PRIORITY_CHOICES),
        required=False,
        label=_('Prioridade')
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Inicial')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Data Final')
    )
    search = forms.CharField(
        required=False,
        label=_('Pesquisar')
    )
