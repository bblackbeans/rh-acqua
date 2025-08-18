from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from utils.decorators import require_ajax, require_role
from utils.forms import ImportForm, ExportForm
from utils.export_import import (
    export_as_csv, export_as_excel, export_as_json, export_as_pdf,
    import_from_csv, import_from_excel, import_from_json
)


@login_required
def export_data(request, model_class, queryset=None, template_name='utils/export.html'):
    """
    View para exportação de dados.
    
    Args:
        request: Objeto de requisição Django
        model_class: Classe do modelo a ser exportado
        queryset: QuerySet a ser exportado (padrão: None, todos os registros)
        template_name: Nome do template (padrão: utils/export.html)
        
    Returns:
        HttpResponse com o template ou arquivo exportado
    """
    # Define os campos disponíveis para exportação
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_class._meta.fields
    ]
    
    # Cria o formulário
    form = ExportForm(request.POST or None, field_choices=field_choices)
    
    if request.method == 'POST' and form.is_valid():
        # Obtém os dados do formulário
        format = form.cleaned_data['format']
        fields = form.cleaned_data['fields'] or [field[0] for field in field_choices]
        
        # Obtém o queryset, se não for fornecido
        if queryset is None:
            queryset = model_class.objects.all()
        
        # Nome do arquivo
        filename = f'export_{model_class._meta.model_name}.{format}'
        
        # Exporta os dados no formato especificado
        if format == 'csv':
            return export_as_csv(queryset, fields=fields, filename=filename)
        elif format == 'excel':
            return export_as_excel(queryset, fields=fields, filename=filename)
        elif format == 'json':
            return export_as_json(queryset, fields=fields, filename=filename)
        elif format == 'pdf':
            # Para PDF, usa um template específico
            template_path = f'utils/export_{model_class._meta.model_name}.html'
            return export_as_pdf(queryset, template_path, filename=filename, context={
                'fields': fields,
                'model_name': model_class._meta.verbose_name_plural
            })
    
    # Renderiza o template
    return render(request, template_name, {
        'form': form,
        'model_name': model_class._meta.verbose_name_plural
    })


@login_required
@require_POST
def import_data(request, model_class, template_name='utils/import.html', redirect_url=None):
    """
    View para importação de dados.
    
    Args:
        request: Objeto de requisição Django
        model_class: Classe do modelo a ser importado
        template_name: Nome do template (padrão: utils/import.html)
        redirect_url: URL para redirecionamento após importação (padrão: None)
        
    Returns:
        HttpResponse com o template ou redirecionamento
    """
    # Cria o formulário
    form = ImportForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        # Obtém o arquivo
        file = request.FILES['file']
        
        # Determina o formato do arquivo
        filename = file.name.lower()
        
        # Importa os dados no formato correto
        if filename.endswith('.csv'):
            created, updated, errors, error_messages = import_from_csv(file, model_class)
        elif filename.endswith('.xlsx'):
            created, updated, errors, error_messages = import_from_excel(file, model_class)
        elif filename.endswith('.json'):
            created, updated, errors, error_messages = import_from_json(file, model_class)
        else:
            return render(request, template_name, {
                'form': form,
                'error': _('Formato de arquivo não suportado.')
            })
        
        # Adiciona mensagens de sucesso/erro
        from django.contrib import messages
        
        if created > 0:
            messages.success(request, _('%(created)d registros criados com sucesso.') % {'created': created})
        
        if updated > 0:
            messages.success(request, _('%(updated)d registros atualizados com sucesso.') % {'updated': updated})
        
        if errors > 0:
            messages.error(request, _('%(errors)d erros encontrados durante a importação.') % {'errors': errors})
            
            # Adiciona detalhes dos erros
            for error in error_messages[:10]:  # Limita a 10 mensagens de erro
                messages.error(request, error)
        
        # Redireciona para a URL especificada ou para a mesma página
        if redirect_url:
            return redirect(redirect_url)
    
    # Renderiza o template
    return render(request, template_name, {
        'form': form,
        'model_name': model_class._meta.verbose_name_plural
    })


@login_required
@require_ajax
def get_cep_info(request):
    """
    View para obter informações de um CEP.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        JsonResponse com as informações do CEP
    """
    import requests
    
    # Obtém o CEP da requisição
    cep = request.GET.get('cep', '').replace('-', '')
    
    # Verifica se o CEP é válido
    if not cep or not cep.isdigit() or len(cep) != 8:
        return JsonResponse({'error': _('CEP inválido.')}, status=400)
    
    try:
        # Consulta a API ViaCEP
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        data = response.json()
        
        # Verifica se houve erro
        if 'erro' in data:
            return JsonResponse({'error': _('CEP não encontrado.')}, status=404)
        
        # Retorna os dados
        return JsonResponse({
            'cep': data.get('cep'),
            'logradouro': data.get('logradouro'),
            'complemento': data.get('complemento'),
            'bairro': data.get('bairro'),
            'cidade': data.get('localidade'),
            'estado': data.get('uf')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_role(['admin'])
def system_info(request):
    """
    View para exibir informações do sistema.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        HttpResponse com as informações do sistema
    """
    import platform
    import django
    import sys
    import psutil
    import os
    
    # Informações do sistema
    system_info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'django_version': django.__version__,
        'hostname': platform.node(),
    }
    
    # Informações de memória
    memory = psutil.virtual_memory()
    memory_info = {
        'total': f"{memory.total / (1024 ** 3):.2f} GB",
        'available': f"{memory.available / (1024 ** 3):.2f} GB",
        'used': f"{memory.used / (1024 ** 3):.2f} GB",
        'percent': f"{memory.percent}%",
    }
    
    # Informações de disco
    disk = psutil.disk_usage('/')
    disk_info = {
        'total': f"{disk.total / (1024 ** 3):.2f} GB",
        'used': f"{disk.used / (1024 ** 3):.2f} GB",
        'free': f"{disk.free / (1024 ** 3):.2f} GB",
        'percent': f"{disk.percent}%",
    }
    
    # Informações de CPU
    cpu_info = {
        'cores_physical': psutil.cpu_count(logical=False),
        'cores_logical': psutil.cpu_count(logical=True),
        'percent': f"{psutil.cpu_percent()}%",
    }
    
    # Informações do Django
    django_info = {
        'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE'),
        'debug': settings.DEBUG,
        'time_zone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
        'database_engine': settings.DATABASES['default']['ENGINE'],
    }
    
    # Renderiza o template
    return render(request, 'utils/system_info.html', {
        'system_info': system_info,
        'memory_info': memory_info,
        'disk_info': disk_info,
        'cpu_info': cpu_info,
        'django_info': django_info,
    })


@login_required
@require_ajax
def validate_cpf(request):
    """
    View para validar um CPF.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        JsonResponse com o resultado da validação
    """
    from utils.helpers import is_valid_cpf
    
    # Obtém o CPF da requisição
    cpf = request.GET.get('cpf', '')
    
    # Valida o CPF
    is_valid = is_valid_cpf(cpf)
    
    return JsonResponse({'is_valid': is_valid})


@login_required
@require_ajax
def validate_cnpj(request):
    """
    View para validar um CNPJ.
    
    Args:
        request: Objeto de requisição Django
        
    Returns:
        JsonResponse com o resultado da validação
    """
    from utils.helpers import is_valid_cnpj
    
    # Obtém o CNPJ da requisição
    cnpj = request.GET.get('cnpj', '')
    
    # Valida o CNPJ
    is_valid = is_valid_cnpj(cnpj)
    
    return JsonResponse({'is_valid': is_valid})


@login_required
def generate_sample_file(request, model_class):
    """
    View para gerar um arquivo de exemplo para importação.
    
    Args:
        request: Objeto de requisição Django
        model_class: Classe do modelo
        
    Returns:
        HttpResponse com o arquivo de exemplo
    """
    from utils.export_import import generate_sample_file
    
    # Obtém o formato do arquivo
    format = request.GET.get('format', 'csv')
    
    # Gera o arquivo de exemplo
    return generate_sample_file(model_class, format=format)
