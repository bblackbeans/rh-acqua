from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    Interview, InterviewFeedback, InterviewQuestion, 
    InterviewTemplate, TemplateQuestion, InterviewSchedule
)


class InterviewForm(forms.ModelForm):
    """
    Formulário para agendamento de entrevistas.
    """
    class Meta:
        model = Interview
        fields = ['application', 'interviewer', 'type', 'scheduled_date', 'duration', 'location', 'meeting_link', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 240}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Adiciona classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name not in ['scheduled_date', 'duration', 'location', 'meeting_link', 'notes']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Se o usuário for um recrutador, filtra as aplicações disponíveis
        if self.user and hasattr(self.user, 'profile') and self.user.profile.role == 'recruiter':
            self.fields['application'].queryset = self.fields['application'].queryset.filter(
                vacancy__recruiter=self.user.profile
            )
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        # Verifica se a data agendada é no futuro
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError(_('A data de agendamento deve ser no futuro.'))
        
        return scheduled_date


class InterviewFeedbackForm(forms.ModelForm):
    """
    Formulário para feedback de entrevistas.
    """
    class Meta:
        model = InterviewFeedback
        fields = ['technical_score', 'communication_score', 'cultural_fit_score', 'strengths', 'weaknesses', 'comments', 'recommendation']
        widgets = {
            'technical_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'communication_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'cultural_fit_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendation': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.interview = kwargs.pop('interview', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.interview:
            instance.interview = self.interview
        if commit:
            instance.save()
        return instance


class InterviewQuestionForm(forms.ModelForm):
    """
    Formulário para perguntas de entrevista.
    """
    class Meta:
        model = InterviewQuestion
        fields = ['text', 'category', 'is_active']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.created_by = self.user.profile
        if commit:
            instance.save()
        return instance


class InterviewTemplateForm(forms.ModelForm):
    """
    Formulário para templates de entrevista.
    """
    class Meta:
        model = InterviewTemplate
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.created_by = self.user.profile
        if commit:
            instance.save()
        return instance


class TemplateQuestionForm(forms.ModelForm):
    """
    Formulário para adicionar perguntas a templates.
    """
    class Meta:
        model = TemplateQuestion
        fields = ['question', 'order']
        widgets = {
            'question': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas perguntas ativas
        self.fields['question'].queryset = self.fields['question'].queryset.filter(is_active=True)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.template:
            instance.template = self.template
        if commit:
            instance.save()
        return instance


class InterviewScheduleForm(forms.ModelForm):
    """
    Formulário para disponibilidade de entrevistadores.
    """
    class Meta:
        model = InterviewSchedule
        fields = ['date', 'start_time', 'end_time', 'is_recurring', 'recurrence_pattern']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_pattern': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_pattern = cleaned_data.get('recurrence_pattern')
        
        # Verifica se o horário de término é posterior ao de início
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_('O horário de término deve ser posterior ao horário de início.'))
        
        # Verifica se o padrão de recorrência foi informado quando necessário
        if is_recurring and not recurrence_pattern:
            raise forms.ValidationError(_('O padrão de recorrência é obrigatório para agendamentos recorrentes.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.interviewer = self.user.profile
        if commit:
            instance.save()
        return instance


class InterviewStatusForm(forms.ModelForm):
    """
    Formulário para atualização de status de entrevista.
    """
    class Meta:
        model = Interview
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
