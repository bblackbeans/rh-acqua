from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Vacancy, Hospital, Department, JobCategory, Skill, VacancyAttachment


class HospitalForm(forms.ModelForm):
    """
    Formulário para criação e edição de hospitais.
    """
    class Meta:
        model = Hospital
        exclude = ('created_at', 'updated_at')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DepartmentForm(forms.ModelForm):
    """
    Formulário para criação e edição de departamentos.
    """
    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }


class JobCategoryForm(forms.ModelForm):
    """
    Formulário para criação e edição de categorias de vagas.
    """
    class Meta:
        model = JobCategory
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    """
    Formulário para criação e edição de habilidades.
    """
    class Meta:
        model = Skill
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class VacancyForm(ModelForm):
    """
    Formulário robusto para criação de vagas com validações e filtros.
    """
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.all().order_by('name'),
        required=True,
        label=_('Hospital/Unidade'),
        help_text=_('Selecione o hospital onde a vaga está disponível'),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'border-radius: 8px; border: 2px solid #e2e8f0; transition: all 0.3s ease;'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        label=_('Departamento/Setor'),
        help_text=_('Selecione o departamento do hospital (opcional)'),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'border-radius: 8px; border: 2px solid #e2e8f0; transition: all 0.3s ease;'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all().order_by('name'),
        required=False,
        label=_('Categoria'),
        help_text=_('Categoria da vaga (opcional)'),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'border-radius: 8px; border: 2px solid #e2e8f0; transition: all 0.3s ease;'
        })
    )
    
    location = forms.CharField(
        max_length=200,
        required=True,
        label=_('Localização'),
        help_text=_('Ex: São Paulo, SP'),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Ex: São Paulo, SP'),
            'style': 'border-radius: 8px; border: 2px solid #e2e8f0; transition: all 0.3s ease;'
        })
    )
    
    # UI simples e infalível para múltipla seleção
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        required=True,
        label=_('Habilidades'),
        help_text=_('Selecione as habilidades necessárias para a vaga'),
        widget=forms.CheckboxSelectMultiple
    )
    
    # Campos obrigatórios que não estão sendo incluídos pelo exclude
    status = forms.ChoiceField(
        choices=[],
        required=True,
        label=_('Status'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    contract_type = forms.ChoiceField(
        choices=[],
        required=True,
        label=_('Tipo de Contrato'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[],
        required=True,
        label=_('Nível de Experiência'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Vacancy
        exclude = ["recruiter", "slug", "created_at", "updated_at", "views_count", "applications_count"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Médico Cardiologista')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Descreva as responsabilidades e atividades da vaga')}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Liste os requisitos mínimos para a vaga')}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Descreva os benefícios oferecidos')}),
            'salary_range_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Salário mínimo')}),
            'salary_range_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Salário máximo')}),
            'monthly_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 40 horas mensais')}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'is_salary_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = kwargs.get("data")
        instance = kwargs.get("instance") or getattr(self, "instance", None)
        hospital_id = None

        if data:
            hospital_id = data.get("hospital") or data.get("hospital_id")
        elif instance and instance.pk:
            hospital_id = instance.hospital_id

        if hospital_id:
            self.fields["department"].queryset = Department.objects.filter(
                hospital_id=hospital_id
            ).order_by('name')
        else:
            self.fields["department"].queryset = Department.objects.all().order_by('name')
        
        # Define valores padrão para campos obrigatórios
        if not data and not instance:
            from vacancies.models import Vacancy
            self.fields['status'].initial = Vacancy.PUBLISHED
            self.fields['contract_type'].initial = Vacancy.FULL_TIME
            self.fields['experience_level'].initial = Vacancy.MID
        
        # Define as choices para os campos
        from vacancies.models import Vacancy
        self.fields['status'].choices = Vacancy.STATUS_CHOICES
        self.fields['contract_type'].choices = Vacancy.CONTRACT_TYPE_CHOICES
        self.fields['experience_level'].choices = Vacancy.EXPERIENCE_LEVEL_CHOICES

    def clean(self):
        cleaned = super().clean()
        h = cleaned.get("hospital")
        d = cleaned.get("department")
        
        if h and d and d.hospital_id != h.id:
            self.add_error("department", _("O departamento não pertence ao hospital selecionado."))
        
        # Validação de datas
        pub_date = cleaned.get("publication_date")
        close_date = cleaned.get("closing_date")
        
        if pub_date and close_date and pub_date >= close_date:
            self.add_error("closing_date", _("A data de encerramento deve ser posterior à data de publicação."))
        
        # Validação de salário
        min_salary = cleaned.get("salary_range_min")
        max_salary = cleaned.get("salary_range_max")
        
        if min_salary and max_salary and min_salary > max_salary:
            self.add_error("salary_range_max", _("O salário máximo deve ser maior que o salário mínimo."))
        
        return cleaned

    def clean_description(self):
        description = self.cleaned_data.get('description')
        # Descrição não é mais obrigatória - apenas retorna o valor
        return description

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        if not skills or skills.count() == 0:
            raise forms.ValidationError(_('Pelo menos uma habilidade deve ser selecionada.'))
        return skills


class VacancyAttachmentForm(forms.ModelForm):
    """
    Formulário para criação e edição de anexos de vagas.
    """
    class Meta:
        model = VacancyAttachment
        exclude = ('vacancy', 'uploaded_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VacancySearchForm(forms.Form):
    """
    Formulário para pesquisa de vagas.
    """
    keyword = forms.CharField(
        label=_('Palavra-chave'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Título, descrição ou requisitos')})
    )
    hospital = forms.ModelChoiceField(
        label=_('Hospital'),
        queryset=Hospital.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        label=_('Categoria'),
        queryset=JobCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    contract_type = forms.ChoiceField(
        label=_('Tipo de contrato'),
        choices=[('', _('Todos'))] + list(Vacancy.CONTRACT_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    experience_level = forms.ChoiceField(
        label=_('Nível de experiência'),
        choices=[('', _('Todos'))] + list(Vacancy.EXPERIENCE_LEVEL_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_remote = forms.BooleanField(
        label=_('Apenas vagas remotas'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
