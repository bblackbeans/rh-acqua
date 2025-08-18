from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    Report, ReportExecution, Dashboard, Widget, 
    Metric, MetricValue, ReportTemplate
)
from users.models import UserProfile


class ReportForm(forms.ModelForm):
    """
    Formulário para criação e edição de relatórios.
    """
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'report_type', 'is_scheduled', 
            'schedule_frequency', 'recipients', 'parameters', 'preferred_format'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'is_scheduled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'schedule_frequency': forms.Select(attrs={'class': 'form-control'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'parameters': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
            'preferred_format': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas usuários ativos
        self.fields['recipients'].queryset = UserProfile.objects.filter(user__is_active=True)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile') and not instance.created_by:
            instance.created_by = self.user.profile
        
        # Atualiza a próxima execução se o relatório for agendado
        if instance.is_scheduled and instance.schedule_frequency:
            now = timezone.now()
            if instance.schedule_frequency == 'daily':
                instance.next_run = now + timezone.timedelta(days=1)
            elif instance.schedule_frequency == 'weekly':
                instance.next_run = now + timezone.timedelta(weeks=1)
            elif instance.schedule_frequency == 'monthly':
                instance.next_run = now + timezone.timedelta(days=30)
            elif instance.schedule_frequency == 'quarterly':
                instance.next_run = now + timezone.timedelta(days=90)
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ReportFilterForm(forms.Form):
    """
    Formulário para filtrar relatórios.
    """
    report_type = forms.ChoiceField(
        label=_('Tipo de Relatório'),
        choices=[('', '----------')] + list(Report.REPORT_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_scheduled = forms.BooleanField(
        label=_('Apenas Agendados'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    created_by = forms.ModelChoiceField(
        label=_('Criado por'),
        queryset=UserProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ReportExecutionForm(forms.ModelForm):
    """
    Formulário para execução de relatórios.
    """
    class Meta:
        model = ReportExecution
        fields = []
    
    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop('report', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.report = self.report
        instance.executed_by = self.user.profile if self.user and hasattr(self.user, 'profile') else None
        instance.status = 'pending'
        
        if commit:
            instance.save()
        return instance


class DashboardForm(forms.ModelForm):
    """
    Formulário para criação e edição de dashboards.
    """
    class Meta:
        model = Dashboard
        fields = ['name', 'description', 'is_public', 'layout']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'layout': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile') and not instance.owner:
            instance.owner = self.user.profile
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
            'title', 'widget_type', 'data_source', 'parameters',
            'position_x', 'position_y', 'width', 'height'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'widget_type': forms.Select(attrs={'class': 'form-control'}),
            'data_source': forms.TextInput(attrs={'class': 'form-control'}),
            'parameters': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
            'position_x': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'position_y': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
        }
    
    def __init__(self, *args, **kwargs):
        self.dashboard = kwargs.pop('dashboard', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.dashboard:
            instance.dashboard = self.dashboard
        if commit:
            instance.save()
        return instance


class MetricForm(forms.ModelForm):
    """
    Formulário para criação e edição de métricas.
    """
    class Meta:
        model = Metric
        fields = [
            'name', 'description', 'metric_type', 'data_source',
            'query', 'parameters'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'metric_type': forms.Select(attrs={'class': 'form-control'}),
            'data_source': forms.TextInput(attrs={'class': 'form-control'}),
            'query': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'parameters': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile') and not instance.created_by:
            instance.created_by = self.user.profile
        if commit:
            instance.save()
        return instance


class MetricValueForm(forms.ModelForm):
    """
    Formulário para criação e edição de valores de métricas.
    """
    class Meta:
        model = MetricValue
        fields = ['date', 'value', 'context']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'context': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.metric = kwargs.pop('metric', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.metric:
            instance.metric = self.metric
        if commit:
            instance.save()
        return instance


class ReportTemplateForm(forms.ModelForm):
    """
    Formulário para criação e edição de templates de relatórios.
    """
    class Meta:
        model = ReportTemplate
        fields = [
            'name', 'description', 'report_type', 'template_file',
            'html_template', 'parameters_schema'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'template_file': forms.FileInput(attrs={'class': 'form-control'}),
            'html_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'parameters_schema': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile') and not instance.created_by:
            instance.created_by = self.user.profile
        if commit:
            instance.save()
        return instance


class ReportParametersForm(forms.Form):
    """
    Formulário dinâmico para parâmetros de relatórios.
    """
    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop('report', None)
        self.template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        # Adiciona campos dinamicamente com base no esquema de parâmetros
        if self.report and self.report.parameters:
            self._add_fields_from_schema(self.report.parameters)
        elif self.template and self.template.parameters_schema:
            self._add_fields_from_schema(self.template.parameters_schema)
    
    def _add_fields_from_schema(self, schema):
        """
        Adiciona campos dinamicamente com base no esquema de parâmetros.
        """
        if not isinstance(schema, dict):
            return
        
        for name, field_def in schema.items():
            field_type = field_def.get('type', 'text')
            label = field_def.get('label', name)
            required = field_def.get('required', False)
            default = field_def.get('default', None)
            choices = field_def.get('choices', None)
            
            if field_type == 'text':
                self.fields[name] = forms.CharField(
                    label=label,
                    required=required,
                    initial=default,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            elif field_type == 'number':
                self.fields[name] = forms.DecimalField(
                    label=label,
                    required=required,
                    initial=default,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
                )
            elif field_type == 'date':
                self.fields[name] = forms.DateField(
                    label=label,
                    required=required,
                    initial=default,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
            elif field_type == 'datetime':
                self.fields[name] = forms.DateTimeField(
                    label=label,
                    required=required,
                    initial=default,
                    widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
                )
            elif field_type == 'boolean':
                self.fields[name] = forms.BooleanField(
                    label=label,
                    required=False,
                    initial=default,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
            elif field_type == 'select' and choices:
                choices_list = [(k, v) for k, v in choices.items()] if isinstance(choices, dict) else choices
                self.fields[name] = forms.ChoiceField(
                    label=label,
                    required=required,
                    initial=default,
                    choices=choices_list,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif field_type == 'multiselect' and choices:
                choices_list = [(k, v) for k, v in choices.items()] if isinstance(choices, dict) else choices
                self.fields[name] = forms.MultipleChoiceField(
                    label=label,
                    required=required,
                    initial=default,
                    choices=choices_list,
                    widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
                )
