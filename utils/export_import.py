import csv
import json
import openpyxl
import pandas as pd
import io
import zipfile
import os
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.core.serializers import serialize
from django.db.models import Model
from django.db.models.query import QuerySet


def export_as_csv(queryset, fields=None, filename='export.csv', exclude=None):
    """
    Exporta um queryset para CSV.
    
    Args:
        queryset: QuerySet a ser exportado
        fields: Lista de campos a serem exportados (padrão: None, todos os campos)
        filename: Nome do arquivo (padrão: export.csv)
        exclude: Lista de campos a serem excluídos (padrão: None)
        
    Returns:
        HttpResponse com o arquivo CSV
    """
    model = queryset.model
    
    if not fields:
        fields = [field.name for field in model._meta.fields]
    
    if exclude:
        fields = [field for field in fields if field not in exclude]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Escreve o cabeçalho
    headers = []
    for field in fields:
        try:
            header = model._meta.get_field(field).verbose_name
        except:
            header = field
        headers.append(str(header))
    
    writer.writerow(headers)
    
    # Escreve os dados
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            if callable(value):
                value = value()
            row.append(str(value) if value is not None else '')
        writer.writerow(row)
    
    return response


def export_as_excel(queryset, fields=None, filename='export.xlsx', exclude=None, sheet_name='Sheet1'):
    """
    Exporta um queryset para Excel.
    
    Args:
        queryset: QuerySet a ser exportado
        fields: Lista de campos a serem exportados (padrão: None, todos os campos)
        filename: Nome do arquivo (padrão: export.xlsx)
        exclude: Lista de campos a serem excluídos (padrão: None)
        sheet_name: Nome da planilha (padrão: Sheet1)
        
    Returns:
        HttpResponse com o arquivo Excel
    """
    model = queryset.model
    
    if not fields:
        fields = [field.name for field in model._meta.fields]
    
    if exclude:
        fields = [field for field in fields if field not in exclude]
    
    # Cria um DataFrame com os dados
    data = []
    for obj in queryset:
        row = {}
        for field in fields:
            value = getattr(obj, field)
            if callable(value):
                value = value()
            row[field] = value
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Renomeia as colunas para os nomes verbosos
    columns = {}
    for field in fields:
        try:
            verbose_name = model._meta.get_field(field).verbose_name
        except:
            verbose_name = field
        columns[field] = str(verbose_name)
    
    df = df.rename(columns=columns)
    
    # Cria o arquivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Configura a resposta HTTP
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_as_json(queryset, fields=None, filename='export.json', exclude=None, indent=4):
    """
    Exporta um queryset para JSON.
    
    Args:
        queryset: QuerySet a ser exportado
        fields: Lista de campos a serem exportados (padrão: None, todos os campos)
        filename: Nome do arquivo (padrão: export.json)
        exclude: Lista de campos a serem excluídos (padrão: None)
        indent: Indentação do JSON (padrão: 4)
        
    Returns:
        HttpResponse com o arquivo JSON
    """
    if fields or exclude:
        # Se campos específicos foram solicitados, serializa manualmente
        data = []
        for obj in queryset:
            item = {}
            for field in (fields or [f.name for f in obj._meta.fields]):
                if exclude and field in exclude:
                    continue
                value = getattr(obj, field)
                if callable(value):
                    value = value()
                item[field] = value
            data.append(item)
        
        json_data = json.dumps(data, indent=indent, default=str)
    else:
        # Caso contrário, usa o serializador do Django
        json_data = serialize('json', queryset, indent=indent)
    
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_as_pdf(queryset, template_path, filename='export.pdf', context=None):
    """
    Exporta um queryset para PDF usando um template.
    
    Args:
        queryset: QuerySet a ser exportado
        template_path: Caminho para o template HTML
        filename: Nome do arquivo (padrão: export.pdf)
        context: Contexto adicional para o template (padrão: None)
        
    Returns:
        HttpResponse com o arquivo PDF
    """
    from django.template.loader import get_template
    from weasyprint import HTML
    
    # Prepara o contexto
    context = context or {}
    context['queryset'] = queryset
    
    # Renderiza o template
    template = get_template(template_path)
    html_string = template.render(context)
    
    # Gera o PDF
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Configura a resposta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_as_zip(files, filename='export.zip'):
    """
    Cria um arquivo ZIP com vários arquivos.
    
    Args:
        files: Dicionário com nomes de arquivos e conteúdos
        filename: Nome do arquivo ZIP (padrão: export.zip)
        
    Returns:
        HttpResponse com o arquivo ZIP
    """
    # Cria o arquivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, file_content in files.items():
            if isinstance(file_content, str):
                # Se for uma string, assume que é um caminho de arquivo
                if os.path.exists(file_content):
                    zip_file.write(file_content, file_name)
            else:
                # Se não for uma string, assume que é o conteúdo do arquivo
                zip_file.writestr(file_name, file_content)
    
    # Configura a resposta HTTP
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def import_from_csv(file, model_class, fields_mapping=None, unique_field=None):
    """
    Importa dados de um arquivo CSV para um modelo.
    
    Args:
        file: Arquivo CSV
        model_class: Classe do modelo
        fields_mapping: Dicionário mapeando colunas do CSV para campos do modelo (padrão: None)
        unique_field: Campo usado para verificar duplicatas (padrão: None)
        
    Returns:
        Tupla com número de registros criados, atualizados e com erro
    """
    created = 0
    updated = 0
    errors = 0
    error_messages = []
    
    # Lê o arquivo CSV
    csv_data = csv.DictReader(file.read().decode('utf-8').splitlines())
    
    for row in csv_data:
        try:
            # Mapeia os campos
            data = {}
            for csv_field, value in row.items():
                if fields_mapping and csv_field in fields_mapping:
                    model_field = fields_mapping[csv_field]
                else:
                    model_field = csv_field
                
                data[model_field] = value
            
            # Verifica se já existe um registro com o campo único
            if unique_field and unique_field in data:
                obj, created_flag = model_class.objects.update_or_create(
                    **{unique_field: data[unique_field]},
                    defaults=data
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            else:
                # Cria um novo registro
                model_class.objects.create(**data)
                created += 1
        
        except Exception as e:
            errors += 1
            error_messages.append(str(e))
    
    return created, updated, errors, error_messages


def import_from_excel(file, model_class, sheet_name=0, fields_mapping=None, unique_field=None):
    """
    Importa dados de um arquivo Excel para um modelo.
    
    Args:
        file: Arquivo Excel
        model_class: Classe do modelo
        sheet_name: Nome ou índice da planilha (padrão: 0, primeira planilha)
        fields_mapping: Dicionário mapeando colunas do Excel para campos do modelo (padrão: None)
        unique_field: Campo usado para verificar duplicatas (padrão: None)
        
    Returns:
        Tupla com número de registros criados, atualizados e com erro
    """
    created = 0
    updated = 0
    errors = 0
    error_messages = []
    
    # Lê o arquivo Excel
    df = pd.read_excel(file, sheet_name=sheet_name)
    
    # Converte o DataFrame para dicionários
    records = df.to_dict('records')
    
    for row in records:
        try:
            # Mapeia os campos
            data = {}
            for excel_field, value in row.items():
                if pd.isna(value):
                    continue
                
                if fields_mapping and excel_field in fields_mapping:
                    model_field = fields_mapping[excel_field]
                else:
                    model_field = excel_field
                
                data[model_field] = value
            
            # Verifica se já existe um registro com o campo único
            if unique_field and unique_field in data:
                obj, created_flag = model_class.objects.update_or_create(
                    **{unique_field: data[unique_field]},
                    defaults=data
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            else:
                # Cria um novo registro
                model_class.objects.create(**data)
                created += 1
        
        except Exception as e:
            errors += 1
            error_messages.append(str(e))
    
    return created, updated, errors, error_messages


def import_from_json(file, model_class, fields_mapping=None, unique_field=None):
    """
    Importa dados de um arquivo JSON para um modelo.
    
    Args:
        file: Arquivo JSON
        model_class: Classe do modelo
        fields_mapping: Dicionário mapeando campos do JSON para campos do modelo (padrão: None)
        unique_field: Campo usado para verificar duplicatas (padrão: None)
        
    Returns:
        Tupla com número de registros criados, atualizados e com erro
    """
    created = 0
    updated = 0
    errors = 0
    error_messages = []
    
    # Lê o arquivo JSON
    json_data = json.loads(file.read().decode('utf-8'))
    
    # Verifica se é uma lista
    if not isinstance(json_data, list):
        json_data = [json_data]
    
    for item in json_data:
        try:
            # Mapeia os campos
            data = {}
            for json_field, value in item.items():
                if fields_mapping and json_field in fields_mapping:
                    model_field = fields_mapping[json_field]
                else:
                    model_field = json_field
                
                data[model_field] = value
            
            # Verifica se já existe um registro com o campo único
            if unique_field and unique_field in data:
                obj, created_flag = model_class.objects.update_or_create(
                    **{unique_field: data[unique_field]},
                    defaults=data
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            else:
                # Cria um novo registro
                model_class.objects.create(**data)
                created += 1
        
        except Exception as e:
            errors += 1
            error_messages.append(str(e))
    
    return created, updated, errors, error_messages


def generate_sample_file(model_class, format='csv', fields=None, exclude=None, filename=None):
    """
    Gera um arquivo de exemplo para importação.
    
    Args:
        model_class: Classe do modelo
        format: Formato do arquivo (csv, excel, json) (padrão: csv)
        fields: Lista de campos a serem incluídos (padrão: None, todos os campos)
        exclude: Lista de campos a serem excluídos (padrão: None)
        filename: Nome do arquivo (padrão: None, gerado automaticamente)
        
    Returns:
        HttpResponse com o arquivo de exemplo
    """
    # Define os campos a serem incluídos
    if not fields:
        fields = [field.name for field in model_class._meta.fields]
    
    if exclude:
        fields = [field for field in fields if field not in exclude]
    
    # Define o nome do arquivo
    if not filename:
        model_name = model_class._meta.model_name
        filename = f'sample_{model_name}.{format}'
    
    # Cria um objeto de exemplo
    sample_obj = model_class()
    
    # Preenche com valores de exemplo
    for field in fields:
        field_obj = model_class._meta.get_field(field)
        
        # Ignora campos auto-incrementáveis
        if field_obj.auto_created:
            continue
        
        # Define um valor de exemplo com base no tipo de campo
        if field_obj.get_internal_type() == 'CharField':
            setattr(sample_obj, field, f'Exemplo {field}')
        elif field_obj.get_internal_type() == 'TextField':
            setattr(sample_obj, field, f'Texto de exemplo para {field}')
        elif field_obj.get_internal_type() in ('IntegerField', 'PositiveIntegerField'):
            setattr(sample_obj, field, 1)
        elif field_obj.get_internal_type() == 'BooleanField':
            setattr(sample_obj, field, True)
        elif field_obj.get_internal_type() == 'DateField':
            setattr(sample_obj, field, '2023-01-01')
        elif field_obj.get_internal_type() == 'DateTimeField':
            setattr(sample_obj, field, '2023-01-01 12:00:00')
        elif field_obj.get_internal_type() == 'EmailField':
            setattr(sample_obj, field, 'exemplo@email.com')
        elif field_obj.get_internal_type() == 'URLField':
            setattr(sample_obj, field, 'https://exemplo.com')
        elif field_obj.get_internal_type() == 'DecimalField':
            setattr(sample_obj, field, '123.45')
        elif field_obj.get_internal_type() == 'ForeignKey':
            setattr(sample_obj, field, 1)
    
    # Cria um queryset com o objeto de exemplo
    queryset = [sample_obj]
    
    # Gera o arquivo no formato especificado
    if format == 'csv':
        return export_as_csv(queryset, fields=fields, filename=filename)
    elif format == 'excel':
        return export_as_excel(queryset, fields=fields, filename=filename)
    elif format == 'json':
        # Para JSON, precisamos serializar manualmente
        data = []
        for obj in queryset:
            item = {}
            for field in fields:
                value = getattr(obj, field)
                if callable(value):
                    value = value()
                item[field] = value
            data.append(item)
        
        json_data = json.dumps(data, indent=4, default=str)
        
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    else:
        raise ValueError(f'Formato não suportado: {format}')
