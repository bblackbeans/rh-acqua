import re
import os
import uuid
import json
import base64
import hashlib
import datetime
from decimal import Decimal
from functools import wraps

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def generate_unique_slug(instance, field_name, new_slug=None):
    """
    Gera um slug único para um modelo.
    
    Args:
        instance: Instância do modelo
        field_name: Nome do campo a ser usado para gerar o slug
        new_slug: Slug personalizado (opcional)
        
    Returns:
        Slug único
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, field_name))
    
    # Obtém o modelo da instância
    model = instance.__class__
    
    # Verifica se já existe um objeto com este slug
    slug_exists = model.objects.filter(slug=slug).exists()
    
    # Se o slug já existe e não é da instância atual, gera um novo
    if slug_exists and (not instance.pk or model.objects.get(slug=slug).pk != instance.pk):
        # Adiciona um UUID aleatório ao slug
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        return generate_unique_slug(instance, field_name, new_slug=slug)
    
    return slug


def format_cpf(cpf):
    """
    Formata um CPF no padrão brasileiro (XXX.XXX.XXX-XX).
    
    Args:
        cpf: CPF a ser formatado
        
    Returns:
        CPF formatado
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return cpf
    
    # Formata o CPF
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def format_cnpj(cnpj):
    """
    Formata um CNPJ no padrão brasileiro (XX.XXX.XXX/XXXX-XX).
    
    Args:
        cnpj: CNPJ a ser formatado
        
    Returns:
        CNPJ formatado
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    
    # Verifica se o CNPJ tem 14 dígitos
    if len(cnpj) != 14:
        return cnpj
    
    # Formata o CNPJ
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def format_cep(cep):
    """
    Formata um CEP no padrão brasileiro (XXXXX-XXX).
    
    Args:
        cep: CEP a ser formatado
        
    Returns:
        CEP formatado
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', str(cep))
    
    # Verifica se o CEP tem 8 dígitos
    if len(cep) != 8:
        return cep
    
    # Formata o CEP
    return f"{cep[:5]}-{cep[5:]}"


def format_phone(phone):
    """
    Formata um número de telefone no padrão brasileiro.
    
    Args:
        phone: Número de telefone a ser formatado
        
    Returns:
        Número de telefone formatado
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', str(phone))
    
    # Verifica o tamanho do número
    if len(phone) == 11:  # Celular com DDD
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:  # Telefone fixo com DDD
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    elif len(phone) == 9:  # Celular sem DDD
        return f"{phone[:5]}-{phone[5:]}"
    elif len(phone) == 8:  # Telefone fixo sem DDD
        return f"{phone[:4]}-{phone[4:]}"
    
    # Retorna o número original se não se encaixar em nenhum padrão
    return phone


def format_currency(value, currency='R$'):
    """
    Formata um valor monetário.
    
    Args:
        value: Valor a ser formatado
        currency: Símbolo da moeda (padrão: R$)
        
    Returns:
        Valor formatado
    """
    try:
        # Converte para Decimal se não for
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Formata o valor
        formatted_value = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Adiciona o símbolo da moeda
        return f"{currency} {formatted_value}"
    except (ValueError, TypeError, InvalidOperation):
        return value


def format_date(date, format_str='%d/%m/%Y'):
    """
    Formata uma data.
    
    Args:
        date: Data a ser formatada
        format_str: String de formato (padrão: %d/%m/%Y)
        
    Returns:
        Data formatada
    """
    if not date:
        return ''
    
    try:
        if isinstance(date, str):
            # Tenta converter a string para data
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        return date.strftime(format_str)
    except (ValueError, AttributeError):
        return date


def format_datetime(dt, format_str='%d/%m/%Y %H:%M'):
    """
    Formata um datetime.
    
    Args:
        dt: Datetime a ser formatado
        format_str: String de formato (padrão: %d/%m/%Y %H:%M)
        
    Returns:
        Datetime formatado
    """
    if not dt:
        return ''
    
    try:
        if isinstance(dt, str):
            # Tenta converter a string para datetime
            dt = datetime.datetime.fromisoformat(dt.replace('Z', '+00:00'))
        
        return dt.strftime(format_str)
    except (ValueError, AttributeError):
        return dt


def get_file_extension(filename):
    """
    Obtém a extensão de um arquivo.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Extensão do arquivo
    """
    return os.path.splitext(filename)[1].lower()


def get_file_size_display(size_bytes):
    """
    Converte o tamanho de um arquivo em bytes para uma representação legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        Tamanho formatado
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def generate_random_token(length=32):
    """
    Gera um token aleatório.
    
    Args:
        length: Comprimento do token (padrão: 32)
        
    Returns:
        Token aleatório
    """
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')[:length]


def hash_password(password):
    """
    Gera um hash seguro para uma senha.
    
    Args:
        password: Senha a ser hasheada
        
    Returns:
        Hash da senha
    """
    # Gera um salt aleatório
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    
    # Gera o hash da senha com o salt
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = base64.b64encode(pwdhash).decode('ascii')
    
    # Retorna o hash no formato salt:hash
    return f"{salt.decode('ascii')}:{pwdhash}"


def verify_password(stored_password, provided_password):
    """
    Verifica se uma senha corresponde ao hash armazenado.
    
    Args:
        stored_password: Hash armazenado
        provided_password: Senha fornecida
        
    Returns:
        True se a senha corresponder, False caso contrário
    """
    # Separa o salt e o hash
    salt, stored_hash = stored_password.split(':')
    
    # Gera o hash da senha fornecida com o mesmo salt
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = base64.b64encode(pwdhash).decode('ascii')
    
    # Compara os hashes
    return pwdhash == stored_hash


def truncate_string(text, max_length=100, suffix='...'):
    """
    Trunca uma string se ela exceder um comprimento máximo.
    
    Args:
        text: Texto a ser truncado
        max_length: Comprimento máximo (padrão: 100)
        suffix: Sufixo a ser adicionado (padrão: ...)
        
    Returns:
        Texto truncado
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def strip_tags(html):
    """
    Remove tags HTML de uma string.
    
    Args:
        html: String HTML
        
    Returns:
        String sem tags HTML
    """
    import re
    return re.sub(r'<[^>]*>', '', html)


def is_valid_cpf(cpf):
    """
    Verifica se um CPF é válido.
    
    Args:
        cpf: CPF a ser verificado
        
    Returns:
        True se o CPF for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito verificador
    if digito1 != int(cpf[9]):
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito verificador
    return digito2 == int(cpf[10])


def is_valid_cnpj(cnpj):
    """
    Verifica se um CNPJ é válido.
    
    Args:
        cnpj: CNPJ a ser verificado
        
    Returns:
        True se o CNPJ for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    
    # Verifica se o CNPJ tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso = 9 if peso == 2 else peso - 1
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito verificador
    if digito1 != int(cnpj[12]):
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso = 9 if peso == 2 else peso - 1
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito verificador
    return digito2 == int(cnpj[13])


def get_client_ip(request):
    """
    Obtém o endereço IP do cliente.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        Endereço IP do cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_browser_info(request):
    """
    Obtém informações sobre o navegador do cliente.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        Dicionário com informações do navegador
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Detecta o navegador
    browser = 'Desconhecido'
    if 'MSIE' in user_agent or 'Trident' in user_agent:
        browser = 'Internet Explorer'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Chrome' in user_agent and 'Edge' not in user_agent:
        browser = 'Chrome'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    elif 'Opera' in user_agent or 'OPR' in user_agent:
        browser = 'Opera'
    
    # Detecta o sistema operacional
    os_name = 'Desconhecido'
    if 'Windows' in user_agent:
        os_name = 'Windows'
    elif 'Macintosh' in user_agent:
        os_name = 'MacOS'
    elif 'Linux' in user_agent:
        os_name = 'Linux'
    elif 'Android' in user_agent:
        os_name = 'Android'
    elif 'iOS' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent:
        os_name = 'iOS'
    
    # Detecta se é um dispositivo móvel
    is_mobile = 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent
    
    return {
        'browser': browser,
        'os': os_name,
        'is_mobile': is_mobile,
        'user_agent': user_agent
    }


def get_base_url(request=None):
    """
    Obtém a URL base do site.
    
    Args:
        request: Objeto de requisição Django (opcional)
        
    Returns:
        URL base do site
    """
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        return f"{protocol}://{domain}"
    
    # Se não houver request, usa as configurações do Django
    protocol = 'https' if settings.SECURE_SSL_REDIRECT else 'http'
    domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
    return f"{protocol}://{domain}"


def json_serialize(obj):
    """
    Serializa um objeto para JSON, lidando com tipos especiais.
    
    Args:
        obj: Objeto a ser serializado
        
    Returns:
        Objeto serializado
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Tipo não serializável: {type(obj)}")


def safe_json_loads(json_str, default=None):
    """
    Carrega uma string JSON de forma segura.
    
    Args:
        json_str: String JSON
        default: Valor padrão em caso de erro (padrão: None)
        
    Returns:
        Objeto JSON ou valor padrão em caso de erro
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj, default=None):
    """
    Converte um objeto para string JSON de forma segura.
    
    Args:
        obj: Objeto a ser convertido
        default: Valor padrão em caso de erro (padrão: None)
        
    Returns:
        String JSON ou valor padrão em caso de erro
    """
    try:
        return json.dumps(obj, default=json_serialize)
    except (TypeError, OverflowError):
        return default


def get_age_from_birth_date(birth_date):
    """
    Calcula a idade a partir da data de nascimento.
    
    Args:
        birth_date: Data de nascimento
        
    Returns:
        Idade em anos
    """
    if not birth_date:
        return None
    
    try:
        if isinstance(birth_date, str):
            # Tenta converter a string para data
            birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = timezone.now().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except (ValueError, AttributeError):
        return None


def get_time_ago(dt):
    """
    Retorna uma string indicando quanto tempo se passou desde uma data.
    
    Args:
        dt: Data/hora
        
    Returns:
        String indicando o tempo decorrido
    """
    if not dt:
        return ''
    
    try:
        if isinstance(dt, str):
            # Tenta converter a string para datetime
            dt = datetime.datetime.fromisoformat(dt.replace('Z', '+00:00'))
        
        now = timezone.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return _('agora mesmo')
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return _('há %(minutes)d minuto(s)') % {'minutes': minutes}
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return _('há %(hours)d hora(s)') % {'hours': hours}
        elif seconds < 604800:
            days = int(seconds // 86400)
            return _('há %(days)d dia(s)') % {'days': days}
        elif seconds < 2592000:
            weeks = int(seconds // 604800)
            return _('há %(weeks)d semana(s)') % {'weeks': weeks}
        elif seconds < 31536000:
            months = int(seconds // 2592000)
            return _('há %(months)d mês(es)') % {'months': months}
        else:
            years = int(seconds // 31536000)
            return _('há %(years)d ano(s)') % {'years': years}
    except (ValueError, AttributeError, TypeError):
        return ''
