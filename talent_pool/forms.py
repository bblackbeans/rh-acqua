from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    TalentPool, Talent, TalentSkill, Tag, TalentTag, 
    TalentNote, SavedSearch, TalentRecommendation
)
from vacancies.models import Skill, Department


class TalentPoolForm(forms.ModelForm):
    """
    Formulário para criação e edição de bancos de talentos.
    """
    class Meta:
        model = TalentPool
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
        if self.user and hasattr(self.user, 'profile') and not instance.created_by:
            instance.created_by = self.user.profile
        if commit:
            instance.save()
        return instance


class TalentForm(forms.ModelForm):
    """
    Formulário para criação e edição de talentos.
    """
    class Meta:
        model = Talent
        fields = [
            'status', 'source', 'notes_content', 'pools', 'departments_of_interest',
            'salary_expectation_min', 'salary_expectation_max', 'available_start_date',
            'last_contact_date'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'notes_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pools': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'departments_of_interest': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'salary_expectation_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_expectation_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_contact_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas bancos de talentos ativos
        self.fields['pools'].queryset = TalentPool.objects.filter(is_active=True)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.candidate:
            instance.candidate = self.candidate
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class TalentSkillForm(forms.ModelForm):
    """
    Formulário para adicionar habilidades a talentos.
    """
    class Meta:
        model = TalentSkill
        fields = ['skill', 'proficiency', 'years_experience', 'is_primary']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-control'}),
            'proficiency': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.5}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.talent = kwargs.pop('talent', None)
        super().__init__(*args, **kwargs)
        
        # Filtra habilidades que o talento ainda não possui
        if self.talent:
            existing_skills = self.talent.skills.all()
            self.fields['skill'].queryset = Skill.objects.exclude(id__in=existing_skills)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.talent:
            instance.talent = self.talent
        if commit:
            instance.save()
        return instance


class TagForm(forms.ModelForm):
    """
    Formulário para criação e edição de tags.
    """
    class Meta:
        model = Tag
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
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


class TalentTagForm(forms.ModelForm):
    """
    Formulário para adicionar tags a talentos.
    """
    class Meta:
        model = TalentTag
        fields = ['tag']
        widgets = {
            'tag': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.talent = kwargs.pop('talent', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra tags que o talento ainda não possui
        if self.talent:
            existing_tags = self.talent.talent_tags.values_list('tag_id', flat=True)
            self.fields['tag'].queryset = Tag.objects.exclude(id__in=existing_tags)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.talent:
            instance.talent = self.talent
        if self.user and hasattr(self.user, 'profile'):
            instance.added_by = self.user.profile
        if commit:
            instance.save()
        return instance


class TalentNoteForm(forms.ModelForm):
    """
    Formulário para adicionar anotações a talentos.
    """
    class Meta:
        model = TalentNote
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.talent = kwargs.pop('talent', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.talent:
            instance.talent = self.talent
        if self.user and hasattr(self.user, 'profile'):
            instance.author = self.user.profile
        if commit:
            instance.save()
        return instance


class SavedSearchForm(forms.ModelForm):
    """
    Formulário para salvar buscas.
    """
    class Meta:
        model = SavedSearch
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.query_params = kwargs.pop('query_params', {})
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'profile'):
            instance.owner = self.user.profile
        instance.query_params = self.query_params
        if commit:
            instance.save()
        return instance


class TalentSearchForm(forms.Form):
    """
    Formulário para busca avançada de talentos.
    """
    keywords = forms.CharField(
        label=_('Palavras-chave'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=Talent.STATUS_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    pools = forms.ModelMultipleChoiceField(
        label=_('Bancos de Talentos'),
        queryset=TalentPool.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    departments = forms.ModelMultipleChoiceField(
        label=_('Departamentos de Interesse'),
        queryset=Department.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    skills = forms.ModelMultipleChoiceField(
        label=_('Habilidades'),
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    tags = forms.ModelMultipleChoiceField(
        label=_('Tags'),
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    min_salary = forms.DecimalField(
        label=_('Salário Mínimo'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_salary = forms.DecimalField(
        label=_('Salário Máximo'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    available_from = forms.DateField(
        label=_('Disponível a partir de'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    last_contact_after = forms.DateField(
        label=_('Último contato após'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    last_contact_before = forms.DateField(
        label=_('Último contato antes de'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class TalentRecommendationForm(forms.ModelForm):
    """
    Formulário para atualizar recomendações de talentos.
    """
    class Meta:
        model = TalentRecommendation
        fields = ['status', 'notes_content', 'match_score']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'match_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        self.talent = kwargs.pop('talent', None)
        self.vacancy = kwargs.pop('vacancy', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.talent:
            instance.talent = self.talent
        if self.vacancy:
            instance.vacancy = self.vacancy
        if self.user and hasattr(self.user, 'profile'):
            instance.recommender = self.user.profile
        if commit:
            instance.save()
        return instance
