from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.conf import settings

from utils.validators import (
    validate_cpf, validate_cnpj, validate_cep, validate_phone,
    validate_password_strength, validate_file_extension, validate_file_size
)


class BaseForm(forms.Form):
    """
    Formulário base com funcionalidades comuns.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona classes CSS aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.EmailInput) or \
               isinstance(field.widget, forms.URLInput) or \
               isinstance(field.widget, forms.PasswordInput) or \
               isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'time'})
            
            # Adiciona placeholder se não existir
            if not field.widget.attrs.get('placeholder') and field.label:
                field.widget.attrs['placeholder'] = field.label


class BaseModelForm(forms.ModelForm):
    """
    Formulário de modelo base com funcionalidades comuns.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona classes CSS aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.EmailInput) or \
               isinstance(field.widget, forms.URLInput) or \
               isinstance(field.widget, forms.PasswordInput) or \
               isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'time'})
            
            # Adiciona placeholder se não existir
            if not field.widget.attrs.get('placeholder') and field.label:
                field.widget.attrs['placeholder'] = field.label


class SlugifyFormMixin:
    """
    Mixin para gerar automaticamente um slug a partir de um campo.
    """
    
    def __init__(self, *args, **kwargs):
        self.slug_field = kwargs.pop('slug_field', 'slug')
        self.slug_source = kwargs.pop('slug_source', 'name')
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Gera o slug se o campo slug estiver vazio
        if self.slug_field in cleaned_data and not cleaned_data.get(self.slug_field):
            source_value = cleaned_data.get(self.slug_source)
            if source_value:
                cleaned_data[self.slug_field] = slugify(source_value)
        
        return cleaned_data


class CPFForm(forms.Form):
    """
    Formulário com campo de CPF.
    """
    cpf = forms.CharField(
        label=_('CPF'),
        max_length=14,
        validators=[validate_cpf],
        widget=forms.TextInput(attrs={'class': 'form-control cpf-mask'})
    )


class CNPJForm(forms.Form):
    """
    Formulário com campo de CNPJ.
    """
    cnpj = forms.CharField(
        label=_('CNPJ'),
        max_length=18,
        validators=[validate_cnpj],
        widget=forms.TextInput(attrs={'class': 'form-control cnpj-mask'})
    )


class CEPForm(forms.Form):
    """
    Formulário com campo de CEP.
    """
    cep = forms.CharField(
        label=_('CEP'),
        max_length=9,
        validators=[validate_cep],
        widget=forms.TextInput(attrs={'class': 'form-control cep-mask'})
    )


class PhoneForm(forms.Form):
    """
    Formulário com campo de telefone.
    """
    phone = forms.CharField(
        label=_('Telefone'),
        max_length=15,
        validators=[validate_phone],
        widget=forms.TextInput(attrs={'class': 'form-control phone-mask'})
    )


class PasswordForm(forms.Form):
    """
    Formulário com campos de senha e confirmação.
    """
    password = forms.CharField(
        label=_('Senha'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password_strength]
    )
    confirm_password = forms.CharField(
        label=_('Confirmar Senha'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError(_('As senhas não coincidem.'))
        
        return cleaned_data


class FileUploadForm(forms.Form):
    """
    Formulário para upload de arquivos.
    """
    file = forms.FileField(
        label=_('Arquivo'),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        self.max_size_mb = kwargs.pop('max_size_mb', None)
        super().__init__(*args, **kwargs)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Valida a extensão do arquivo
            if self.allowed_extensions:
                validate_file_extension(file, self.allowed_extensions)
            
            # Valida o tamanho do arquivo
            if self.max_size_mb:
                validate_file_size(file, self.max_size_mb)
        
        return file


class ImageUploadForm(FileUploadForm):
    """
    Formulário para upload de imagens.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['.jpg', '.jpeg', '.png', '.gif'])
        kwargs.setdefault('max_size_mb', 5)
        super().__init__(*args, **kwargs)
        self.fields['file'].label = _('Imagem')


class DocumentUploadForm(FileUploadForm):
    """
    Formulário para upload de documentos.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'])
        kwargs.setdefault('max_size_mb', 10)
        super().__init__(*args, **kwargs)
        self.fields['file'].label = _('Documento')


class DateRangeForm(forms.Form):
    """
    Formulário com campos de data inicial e final.
    """
    start_date = forms.DateField(
        label=_('Data Inicial'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label=_('Data Final'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError(_('A data inicial não pode ser posterior à data final.'))
        
        return cleaned_data


class SearchForm(forms.Form):
    """
    Formulário de pesquisa.
    """
    q = forms.CharField(
        label=_('Pesquisar'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Pesquisar...'),
        })
    )


class AdvancedSearchForm(forms.Form):
    """
    Formulário de pesquisa avançada.
    """
    q = forms.CharField(
        label=_('Pesquisar'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Pesquisar...'),
        })
    )
    
    date_from = forms.DateField(
        label=_('Data Inicial'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        label=_('Data Final'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    order_by = forms.ChoiceField(
        label=_('Ordenar por'),
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        order_choices = kwargs.pop('order_choices', [])
        super().__init__(*args, **kwargs)
        
        if order_choices:
            self.fields['order_by'].choices = order_choices
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError(_('A data inicial não pode ser posterior à data final.'))
        
        return cleaned_data


class ImportForm(forms.Form):
    """
    Formulário para importação de dados.
    """
    file = forms.FileField(
        label=_('Arquivo'),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', ['.csv', '.xlsx', '.json'])
        self.max_size_mb = kwargs.pop('max_size_mb', 10)
        super().__init__(*args, **kwargs)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Valida a extensão do arquivo
            validate_file_extension(file, self.allowed_extensions)
            
            # Valida o tamanho do arquivo
            validate_file_size(file, self.max_size_mb)
        
        return file


class ExportForm(forms.Form):
    """
    Formulário para exportação de dados.
    """
    format = forms.ChoiceField(
        label=_('Formato'),
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('json', 'JSON'),
            ('pdf', 'PDF'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fields = forms.MultipleChoiceField(
        label=_('Campos'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        field_choices = kwargs.pop('field_choices', [])
        super().__init__(*args, **kwargs)
        
        if field_choices:
            self.fields['fields'].choices = field_choices
