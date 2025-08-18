from django import template
import re

register = template.Library()

def digits(v): 
    return re.sub(r'\D','', str(v or ''))

@register.filter
def mask_cpf(v):
    d = digits(v)
    if len(d) < 11:
        return d
    return f'{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}'

@register.filter
def mask_pis(v):
    d = digits(v)
    if len(d) < 11:
        return d
    return f'{d[:3]}.{d[3:8]}.{d[8:10]}-{d[10:]}'

@register.filter
def mask_phone(v):
    d = digits(v)
    if len(d) < 10:
        return d
    if len(d) == 11:
        return f'({d[:2]}) {d[2:7]}-{d[7:]}'
    else:  # 10 dígitos
        return f'({d[:2]}) {d[2:6]}-{d[6:]}'

@register.filter
def mask_cep(v):
    d = digits(v)
    if len(d) < 8:
        return d
    return f'{d[:5]}-{d[5:]}'

@register.filter
def mask_rg(v):
    d = digits(v)
    return d  # RG sem máscara, apenas números 