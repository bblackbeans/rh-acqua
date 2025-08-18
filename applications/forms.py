from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Application, ApplicationEvaluation, Resume, Education, WorkExperience


class ApplicationForm(forms.ModelForm):
    """
    Formulário para candidaturas a vagas.
    """
    class Meta:
        model = Application
        fields = ['vacancy', 'cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        
        # Adiciona classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name != 'resume':
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.candidate:
            instance.candidate = self.candidate
        if commit:
            instance.save()
        return instance


class ApplicationEvaluationForm(forms.ModelForm):
    """
    Formulário para avaliação de candidaturas.
    """
    class Meta:
        model = ApplicationEvaluation
        fields = ['technical_score', 'experience_score', 'cultural_fit_score', 'comments']
        widgets = {
            'technical_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'class': 'form-control'}),
            'experience_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'class': 'form-control'}),
            'cultural_fit_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.evaluator = kwargs.pop('evaluator', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.application:
            instance.application = self.application
        if self.evaluator:
            instance.evaluator = self.evaluator
        if commit:
            instance.save()
        return instance


class ResumeForm(forms.ModelForm):
    """
    Formulário para currículos detalhados.
    """
    class Meta:
        model = Resume
        fields = ['summary', 'skills', 'languages', 'certifications']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'languages': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.candidate:
            instance.candidate = self.candidate
        if commit:
            instance.save()
        return instance


class EducationForm(forms.ModelForm):
    """
    Formulário para formação educacional.
    """
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.Select(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.resume = kwargs.pop('resume', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.resume:
            instance.resume = self.resume
        if commit:
            instance.save()
        return instance


class WorkExperienceForm(forms.ModelForm):
    """
    Formulário para experiências profissionais.
    """
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'start_date', 'end_date', 'is_current', 'description', 'achievements']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.resume = kwargs.pop('resume', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.resume:
            instance.resume = self.resume
        if commit:
            instance.save()
        return instance


class ApplicationStatusForm(forms.ModelForm):
    """
    Formulário para atualização de status de candidatura.
    """
    class Meta:
        model = Application
        fields = ['status', 'recruiter_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'recruiter_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
