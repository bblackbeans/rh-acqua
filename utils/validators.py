from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from utils.helpers import is_valid_cpf, is_valid_cnpj


# Validadores de expressão regular
# cpf_validator removido para aceitar qualquer formato (máscaras aplicadas no frontend)

cnpj_validator = RegexValidator(
    regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$',
    message=_('CNPJ inválido. Use o formato XX.XXX.XXX/XXXX-XX ou apenas números.')
)

# cep_validator removido para aceitar qualquer formato (máscaras aplicadas no frontend)
# phone_validator removido para aceitar qualquer formato (máscaras aplicadas no frontend)

date_validator = RegexValidator(
    regex=r'^\d{2}/\d{2}/\d{4}$',
    message=_('Data inválida. Use o formato DD/MM/AAAA.')
)

time_validator = RegexValidator(
    regex=r'^\d{2}:\d{2}(:\d{2})?$',
    message=_('Hora inválida. Use o formato HH:MM ou HH:MM:SS.')
)

color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    message=_('Cor inválida. Use o formato hexadecimal (#RRGGBB ou #RGB).')
)

url_validator = RegexValidator(
    regex=r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$',
    message=_('URL inválida.')
)

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,30}$',
    message=_('Nome de usuário inválido. Use apenas letras, números e underscores. Entre 3 e 30 caracteres.')
)

password_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
    message=_('Senha inválida. Deve conter pelo menos 8 caracteres, incluindo letras e números.')
)

slug_validator = RegexValidator(
    regex=r'^[a-z0-9-]+$',
    message=_('Slug inválido. Use apenas letras minúsculas, números e hífens.')
)


# Validadores personalizados
def validate_cpf(value):
    """
    Valida um CPF.
    
    Args:
        value: CPF a ser validado
        
    Raises:
        ValidationError: Se o CPF for inválido
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se o CPF é válido
    if not is_valid_cpf(cpf):
        raise ValidationError(_('CPF inválido.'))


def validate_cnpj(value):
    """
    Valida um CNPJ.
    
    Args:
        value: CNPJ a ser validado
        
    Raises:
        ValidationError: Se o CNPJ for inválido
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se o CNPJ é válido
    if not is_valid_cnpj(cnpj):
        raise ValidationError(_('CNPJ inválido.'))


def validate_cep(value):
    """
    Valida um CEP.
    
    Args:
        value: CEP a ser validado
        
    Raises:
        ValidationError: Se o CEP for inválido
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se o CEP tem 8 dígitos
    if len(cep) != 8:
        raise ValidationError(_('CEP inválido. Deve conter 8 dígitos.'))


def validate_phone(value):
    """
    Valida um número de telefone.
    
    Args:
        value: Número de telefone a ser validado
        
    Raises:
        ValidationError: Se o número de telefone for inválido
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', str(value))
    
    # Verifica se o telefone tem entre 10 e 11 dígitos
    if len(phone) < 10 or len(phone) > 11:
        raise ValidationError(_('Telefone inválido. Deve conter entre 10 e 11 dígitos.'))


def validate_future_date(value):
    """
    Valida se uma data é futura.
    
    Args:
        value: Data a ser validada
        
    Raises:
        ValidationError: Se a data não for futura
    """
    from django.utils import timezone
    
    if value <= timezone.now().date():
        raise ValidationError(_('A data deve ser futura.'))


def validate_past_date(value):
    """
    Valida se uma data é passada.
    
    Args:
        value: Data a ser validada
        
    Raises:
        ValidationError: Se a data não for passada
    """
    from django.utils import timezone
    
    if value >= timezone.now().date():
        raise ValidationError(_('A data deve ser passada.'))


def validate_age(value, min_age=18, max_age=None):
    """
    Valida a idade com base na data de nascimento.
    
    Args:
        value: Data de nascimento
        min_age: Idade mínima (padrão: 18)
        max_age: Idade máxima (padrão: None)
        
    Raises:
        ValidationError: Se a idade não estiver dentro do intervalo especificado
    """
    from django.utils import timezone
    from utils.helpers import get_age_from_birth_date
    
    age = get_age_from_birth_date(value)
    
    if age is None:
        raise ValidationError(_('Data de nascimento inválida.'))
    
    if age < min_age:
        raise ValidationError(_('Idade mínima: %(min_age)d anos.') % {'min_age': min_age})
    
    if max_age is not None and age > max_age:
        raise ValidationError(_('Idade máxima: %(max_age)d anos.') % {'max_age': max_age})


def validate_file_extension(value, allowed_extensions):
    """
    Valida a extensão de um arquivo.
    
    Args:
        value: Arquivo a ser validado
        allowed_extensions: Lista de extensões permitidas
        
    Raises:
        ValidationError: Se a extensão do arquivo não for permitida
    """
    import os
    
    # Obtém a extensão do arquivo
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _('Extensão de arquivo não permitida. As extensões permitidas são: %(extensions)s.') % {
                'extensions': ', '.join(allowed_extensions)
            }
        )


def validate_file_size(value, max_size_mb):
    """
    Valida o tamanho de um arquivo.
    
    Args:
        value: Arquivo a ser validado
        max_size_mb: Tamanho máximo em MB
        
    Raises:
        ValidationError: Se o tamanho do arquivo exceder o limite
    """
    # Converte MB para bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if value.size > max_size_bytes:
        raise ValidationError(
            _('O tamanho do arquivo não pode exceder %(max_size)s MB.') % {
                'max_size': max_size_mb
            }
        )


def validate_image_dimensions(value, min_width=None, min_height=None, max_width=None, max_height=None):
    """
    Valida as dimensões de uma imagem.
    
    Args:
        value: Imagem a ser validada
        min_width: Largura mínima (padrão: None)
        min_height: Altura mínima (padrão: None)
        max_width: Largura máxima (padrão: None)
        max_height: Altura máxima (padrão: None)
        
    Raises:
        ValidationError: Se as dimensões da imagem não estiverem dentro dos limites especificados
    """
    from PIL import Image
    
    # Abre a imagem
    img = Image.open(value)
    width, height = img.size
    
    if min_width is not None and width < min_width:
        raise ValidationError(
            _('A largura da imagem deve ser de pelo menos %(min_width)d pixels.') % {
                'min_width': min_width
            }
        )
    
    if min_height is not None and height < min_height:
        raise ValidationError(
            _('A altura da imagem deve ser de pelo menos %(min_height)d pixels.') % {
                'min_height': min_height
            }
        )
    
    if max_width is not None and width > max_width:
        raise ValidationError(
            _('A largura da imagem não pode exceder %(max_width)d pixels.') % {
                'max_width': max_width
            }
        )
    
    if max_height is not None and height > max_height:
        raise ValidationError(
            _('A altura da imagem não pode exceder %(max_height)d pixels.') % {
                'max_height': max_height
            }
        )


def validate_password_strength(value):
    """
    Valida a força de uma senha.
    
    Args:
        value: Senha a ser validada
        
    Raises:
        ValidationError: Se a senha não atender aos requisitos de força
    """
    # Verifica o comprimento mínimo
    if len(value) < 8:
        raise ValidationError(_('A senha deve conter pelo menos 8 caracteres.'))
    
    # Verifica se contém pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('A senha deve conter pelo menos uma letra maiúscula.'))
    
    # Verifica se contém pelo menos uma letra minúscula
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('A senha deve conter pelo menos uma letra minúscula.'))
    
    # Verifica se contém pelo menos um número
    if not re.search(r'\d', value):
        raise ValidationError(_('A senha deve conter pelo menos um número.'))
    
    # Verifica se contém pelo menos um caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('A senha deve conter pelo menos um caractere especial.'))


def validate_unique_together(model, fields, values, exclude_id=None):
    """
    Valida se a combinação de campos é única.
    
    Args:
        model: Modelo Django
        fields: Lista de campos
        values: Lista de valores
        exclude_id: ID a ser excluído da validação (padrão: None)
        
    Raises:
        ValidationError: Se a combinação de campos não for única
    """
    # Cria o filtro
    filters = {}
    for field, value in zip(fields, values):
        filters[field] = value
    
    # Exclui o ID, se fornecido
    if exclude_id is not None:
        query = model.objects.filter(**filters).exclude(id=exclude_id)
    else:
        query = model.objects.filter(**filters)
    
    # Verifica se já existe um objeto com esta combinação de campos
    if query.exists():
        raise ValidationError(
            _('Já existe um registro com esta combinação de %(fields)s.') % {
                'fields': ', '.join(fields)
            }
        )


def validate_json(value):
    """
    Valida se uma string é um JSON válido.
    
    Args:
        value: String a ser validada
        
    Raises:
        ValidationError: Se a string não for um JSON válido
    """
    import json
    
    try:
        json.loads(value)
    except json.JSONDecodeError:
        raise ValidationError(_('JSON inválido.'))


def validate_url_exists(value):
    """
    Valida se uma URL existe.
    
    Args:
        value: URL a ser validada
        
    Raises:
        ValidationError: Se a URL não existir
    """
    import requests
    
    try:
        response = requests.head(value, timeout=5)
        if response.status_code >= 400:
            raise ValidationError(_('URL não encontrada.'))
    except requests.RequestException:
        raise ValidationError(_('Não foi possível acessar a URL.'))
