from functools import wraps
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import PermissionDenied


def require_ajax(view_func):
    """
    Decorador que verifica se a requisição é AJAX.
    
    Args:
        view_func: Função de view a ser decorada
        
    Returns:
        Função decorada
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': _('Requisição AJAX necessária')}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper


def require_post(view_func):
    """
    Decorador que verifica se a requisição é POST.
    
    Args:
        view_func: Função de view a ser decorada
        
    Returns:
        Função decorada
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({'error': _('Método POST necessário')}, status=405)
        return view_func(request, *args, **kwargs)
    return wrapper


def require_role(roles):
    """
    Decorador que verifica se o usuário tem um dos perfis especificados.
    
    Args:
        roles: Lista de perfis permitidos
        
    Returns:
        Decorador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
            
            if not hasattr(request.user, 'profile'):
                return HttpResponseRedirect(reverse('login'))
            
            if request.user.profile.role not in roles:
                messages.error(request, _('Você não tem permissão para acessar esta página.'))
                return HttpResponseRedirect(reverse('dashboard'))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission):
    """
    Decorador que verifica se o usuário tem a permissão especificada.
    
    Args:
        permission: Permissão necessária
        
    Returns:
        Decorador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
            
            if not request.user.has_perm(permission):
                messages.error(request, _('Você não tem permissão para acessar esta página.'))
                return HttpResponseRedirect(reverse('dashboard'))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_superuser(view_func):
    """
    Decorador que verifica se o usuário é superusuário.
    
    Args:
        view_func: Função de view a ser decorada
        
    Returns:
        Função decorada
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        
        if not request.user.is_superuser:
            messages.error(request, _('Apenas superusuários podem acessar esta página.'))
            return HttpResponseRedirect(reverse('dashboard'))
        
        return view_func(request, *args, **kwargs)
    return wrapper


def cache_page_for_user(timeout):
    """
    Decorador que faz cache de uma página por usuário.
    
    Args:
        timeout: Tempo de cache em segundos
        
    Returns:
        Decorador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from django.utils.cache import patch_response_headers
            from django.core.cache import cache
            
            # Gera uma chave de cache única para o usuário e a URL
            if request.user.is_authenticated:
                cache_key = f"user_{request.user.id}_{request.path}"
            else:
                cache_key = f"anonymous_{request.path}"
            
            # Tenta obter a resposta do cache
            response = cache.get(cache_key)
            
            if response is None:
                # Se não estiver no cache, gera a resposta
                response = view_func(request, *args, **kwargs)
                
                # Adiciona cabeçalhos de cache
                patch_response_headers(response, timeout)
                
                # Armazena no cache
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def log_activity(activity_type):
    """
    Decorador que registra a atividade do usuário.
    
    Args:
        activity_type: Tipo de atividade
        
    Returns:
        Decorador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Executa a view
            response = view_func(request, *args, **kwargs)
            
            # Registra a atividade apenas se o usuário estiver autenticado
            if request.user.is_authenticated:
                try:
                    from administration.models import ActivityLog
                    
                    # Obtém o endereço IP
                    from utils.helpers import get_client_ip
                    ip = get_client_ip(request)
                    
                    # Obtém informações do navegador
                    from utils.helpers import get_browser_info
                    browser_info = get_browser_info(request)
                    
                    # Cria o registro de atividade
                    ActivityLog.objects.create(
                        user=request.user,
                        activity_type=activity_type,
                        ip_address=ip,
                        browser=browser_info['browser'],
                        os=browser_info['os'],
                        user_agent=browser_info['user_agent'],
                        url=request.path,
                        method=request.method
                    )
                except ImportError:
                    # Se o modelo ActivityLog não estiver disponível, ignora
                    pass
                except Exception as e:
                    # Ignora erros para não afetar a resposta
                    if settings.DEBUG:
                        print(f"Erro ao registrar atividade: {e}")
            
            return response
        return wrapper
    return decorator


def rate_limit(num_requests, period):
    """
    Decorador que limita o número de requisições por período.
    
    Args:
        num_requests: Número máximo de requisições
        period: Período em segundos
        
    Returns:
        Decorador
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from django.core.cache import cache
            
            # Gera uma chave de cache única para o usuário e a view
            if request.user.is_authenticated:
                cache_key = f"rate_limit_{request.user.id}_{view_func.__name__}"
            else:
                # Para usuários não autenticados, usa o IP
                from utils.helpers import get_client_ip
                ip = get_client_ip(request)
                cache_key = f"rate_limit_{ip}_{view_func.__name__}"
            
            # Obtém o contador atual
            requests = cache.get(cache_key, [])
            
            # Remove requisições antigas
            now = datetime.datetime.now().timestamp()
            requests = [req for req in requests if req > now - period]
            
            # Verifica se excedeu o limite
            if len(requests) >= num_requests:
                return JsonResponse({
                    'error': _('Limite de requisições excedido. Tente novamente mais tarde.')
                }, status=429)
            
            # Adiciona a requisição atual
            requests.append(now)
            
            # Atualiza o cache
            cache.set(cache_key, requests, period)
            
            # Executa a view
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def track_page_view(view_func):
    """
    Decorador que registra visualizações de página.
    
    Args:
        view_func: Função de view a ser decorada
        
    Returns:
        Função decorada
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Executa a view
        response = view_func(request, *args, **kwargs)
        
        # Registra a visualização apenas se for uma requisição GET bem-sucedida
        if request.method == 'GET' and response.status_code == 200:
            try:
                from administration.models import PageView
                
                # Obtém o endereço IP
                from utils.helpers import get_client_ip
                ip = get_client_ip(request)
                
                # Obtém informações do navegador
                from utils.helpers import get_browser_info
                browser_info = get_browser_info(request)
                
                # Cria o registro de visualização
                PageView.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    url=request.path,
                    ip_address=ip,
                    browser=browser_info['browser'],
                    os=browser_info['os'],
                    is_mobile=browser_info['is_mobile'],
                    referrer=request.META.get('HTTP_REFERER', '')
                )
            except ImportError:
                # Se o modelo PageView não estiver disponível, ignora
                pass
            except Exception as e:
                # Ignora erros para não afetar a resposta
                if settings.DEBUG:
                    print(f"Erro ao registrar visualização de página: {e}")
        
        return response
    return wrapper
