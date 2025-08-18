from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _

from .models import User, CandidateProfile, RecruiterProfile, Education, Experience, TechnicalSkill, SoftSkill, Certification, Language


class CustomUserCreationForm(UserCreationForm):
    """
    Formulário para criação de novos usuários com campos personalizados.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')
        

class CustomUserChangeForm(UserChangeForm):
    """
    Formulário para atualização de usuários existentes.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'phone', 'date_of_birth', 'profile_picture', 'bio')


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulário de autenticação personalizado usando email em vez de username.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': _('Email')}),
    )
    password = forms.CharField(
        label=_("Senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Senha')}),
    )


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulário de redefinição de senha personalizado.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulário para definir uma nova senha personalizado.
    """
    new_password1 = forms.CharField(
        label=_("Nova senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Nova senha')}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Confirme a nova senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirme a nova senha')}),
    )


class CandidateProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil de candidato.
    """
    class Meta:
        model = CandidateProfile
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'desired_position': forms.TextInput(attrs={'class': 'form-control'}),
            'desired_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_immediately': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notice_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class RecruiterProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil de recrutador.
    """
    class Meta:
        model = RecruiterProfile
        exclude = ('user', 'created_at', 'updated_at', 'vacancies_created', 'candidates_interviewed', 'successful_hires')
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'hiring_authority': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserRegistrationForm(forms.ModelForm):
    """
    Formulário para registro de novos usuários no site.
    """
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
    )
    first_name = forms.CharField(
        label=_("Nome"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nome')}),
    )
    last_name = forms.CharField(
        label=_("Sobrenome"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Sobrenome')}),
    )
    password1 = forms.CharField(
        label=_("Senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Senha')}),
    )
    password2 = forms.CharField(
        label=_("Confirme a senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirme a senha')}),
        strip=False,
    )
    role = forms.ChoiceField(
        label=_("Tipo de conta"),
        choices=[('candidate', _('Candidato'))],  # Apenas candidato disponível
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='candidate',
        required=False,  # Não é obrigatório no formulário, será definido na view
        help_text=_("Por enquanto, apenas candidatos podem se registrar.")
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')
    
    def clean(self):
        """
        Limpa e valida todos os campos do formulário.
        """
        cleaned_data = super().clean()
        # Força o papel de candidato para todos os registros
        cleaned_data['role'] = 'candidate'
        return cleaned_data
    
    def clean_password2(self):
        """
        Valida se as senhas coincidem e se atendem aos requisitos mínimos.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("As senhas não coincidem."),
                code="password_mismatch",
            )
        
        # Validação básica de força da senha
        if password2:
            if len(password2) < 8:
                raise forms.ValidationError(
                    _("A senha deve conter pelo menos 8 caracteres."),
                    code="password_too_short",
                )
            if not any(c.isupper() for c in password2):
                raise forms.ValidationError(
                    _("A senha deve conter pelo menos uma letra maiúscula."),
                    code="password_no_upper",
                )
            if not any(c.islower() for c in password2):
                raise forms.ValidationError(
                    _("A senha deve conter pelo menos uma letra minúscula."),
                    code="password_no_lower",
                )
            if not any(c.isdigit() for c in password2):
                raise forms.ValidationError(
                    _("A senha deve conter pelo menos um número."),
                    code="password_no_digit",
                )
        
        return password2
    
    def save(self, commit=True):
        """
        Salva o usuário com a senha criptografada.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EducationForm(forms.ModelForm):
    """Formulário para formação acadêmica."""
    
    class Meta:
        model = Education
        fields = ['instituicao', 'curso', 'nivel', 'inicio', 'fim', 'em_andamento']
        widgets = {
            'instituicao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da instituição'}),
            'curso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do curso'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'em_andamento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        fim = cleaned_data.get('fim')
        em_andamento = cleaned_data.get('em_andamento')
        
        if not em_andamento and not fim:
            raise forms.ValidationError(_('Informe a data de conclusão ou marque como em andamento.'))
        
        if fim and inicio and fim < inicio:
            raise forms.ValidationError(_('A data de conclusão não pode ser anterior à data de início.'))
        
        return cleaned_data


class ExperienceForm(forms.ModelForm):
    """Formulário para experiência profissional."""
    
    class Meta:
        model = Experience
        fields = ['empresa', 'cargo', 'inicio', 'fim', 'atual', 'atividades']
        widgets = {
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo/função'}),
            'inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'atual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'atividades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Principais atividades e responsabilidades'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        fim = cleaned_data.get('fim')
        atual = cleaned_data.get('atual')
        
        if not atual and not fim:
            raise forms.ValidationError(_('Informe a data de saída ou marque como trabalho atual.'))
        
        if fim and inicio and fim < inicio:
            raise forms.ValidationError(_('A data de saída não pode ser anterior à data de início.'))
        
        return cleaned_data


class TechnicalSkillForm(forms.ModelForm):
    """Formulário para habilidades técnicas."""
    
    class Meta:
        model = TechnicalSkill
        fields = ['nome', 'nivel']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da habilidade técnica'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }


class SoftSkillForm(forms.ModelForm):
    """Formulário para habilidades emocionais."""
    
    class Meta:
        model = SoftSkill
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da habilidade emocional'}),
        }


class CertificationForm(forms.ModelForm):
    """Formulário para certificações."""
    
    class Meta:
        model = Certification
        fields = ['titulo', 'orgao', 'emissao', 'validade', 'sem_validade', 'credencial_url']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da certificação'}),
            'orgao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Órgão emissor'}),
            'emissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sem_validade': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'sem_validade'}),
            'credencial_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL da credencial (opcional)'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        emissao = cleaned_data.get('emissao')
        validade = cleaned_data.get('validade')
        sem_validade = cleaned_data.get('sem_validade')
        
        # Se marcou "sem data de validade", limpa o campo validade
        if sem_validade:
            cleaned_data['validade'] = None
        
        # Validação: se não marcou "sem data de validade", a data de validade é obrigatória
        if not sem_validade and not validade:
            raise forms.ValidationError(_('Informe a data de validade ou marque como "sem data de validade".'))
        
        if validade and emissao and validade < emissao:
            raise forms.ValidationError(_('A data de validade não pode ser anterior à data de emissão.'))
        
        return cleaned_data


class LanguageForm(forms.ModelForm):
    """Formulário para idiomas."""
    
    class Meta:
        model = Language
        fields = ['idioma', 'idioma_outro', 'nivel']
        widgets = {
            'idioma': forms.Select(attrs={'class': 'form-select', 'id': 'idioma_select'}),
            'idioma_outro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do idioma', 'id': 'idioma_outro_field'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        idioma = cleaned_data.get('idioma')
        idioma_outro = cleaned_data.get('idioma_outro')
        
        # Se selecionou "outro", o campo idioma_outro é obrigatório
        if idioma == 'outro' and not idioma_outro:
            raise forms.ValidationError(_('Informe o nome do idioma quando selecionar "Outro".'))
        
        # Se não selecionou "outro", limpa o campo idioma_outro
        if idioma != 'outro':
            cleaned_data['idioma_outro'] = None
        
        # Validação de idioma duplicado
        if self.instance.pk:  # Editando
            user = self.instance.user
        else:  # Criando novo
            user = getattr(self, 'user', None)
        
        if user and idioma:
            # Verifica se já existe um idioma igual para este usuário
            existing_language = Language.objects.filter(
                user=user,
                idioma=idioma
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing_language.exists():
                if idioma == 'outro' and idioma_outro:
                    raise forms.ValidationError(_(f'Você já tem o idioma "{idioma_outro}" cadastrado.'))
                else:
                    idioma_display = dict(Language.IDIOMA_CHOICES).get(idioma, idioma)
                    raise forms.ValidationError(_(f'Você já tem o idioma "{idioma_display}" cadastrado.'))
        
        return cleaned_data
