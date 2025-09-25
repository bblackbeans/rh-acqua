from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import time
import re
import json
from utils.helpers import get_client_ip, get_browser_info


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware para modo de manutenção.
    Redireciona todas as requisições para uma página de manutenção
    quando o modo de manutenção está ativado.
    """
    
    def process_request(self, request):
        # Verifica se o modo de manutenção está ativado
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Verifica se o usuário está na lista de IPs permitidos
            client_ip = get_client_ip(request)
            allowed_ips = getattr(settings, 'MAINTENANCE_ALLOWED_IPS', [])
            
            if client_ip not in allowed_ips:
                # Verifica se a requisição é para a página de manutenção
                maintenance_url = getattr(settings, 'MAINTENANCE_URL', '/maintenance/')
                if request.path != maintenance_url:
                    # Se for uma requisição AJAX, retorna um erro JSON
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'error': _('Sistema em manutenção. Tente novamente mais tarde.')
                        }, status=503)
                    
                    # Redireciona para a página de manutenção
                    return HttpResponseRedirect(maintenance_url)
        
        return None


class RequestTimeMiddleware(MiddlewareMixin):
    """
    Middleware para medir o tempo de processamento das requisições.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            # Calcula o tempo de processamento
            duration = time.time() - request.start_time
            
            # Adiciona o tempo de processamento ao cabeçalho da resposta
            response['X-Processing-Time'] = f"{duration:.4f}s"
            
            # Registra requisições lentas
            if duration > getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0):
                self._log_slow_request(request, duration)
        
        return response
    
    def _log_slow_request(self, request, duration):
        """
        Registra requisições lentas.
        """
        try:
            from administration.models import SlowRequest
            
            # Obtém o endereço IP
            ip = get_client_ip(request)
            
            # Obtém informações do navegador
            browser_info = get_browser_info(request)
            
            # Cria o registro de requisição lenta
            SlowRequest.objects.create(
                user=request.user if request.user.is_authenticated else None,
                url=request.path,
                method=request.method,
                duration=duration,
                ip_address=ip,
                browser=browser_info['browser'],
                os=browser_info['os'],
                user_agent=browser_info['user_agent']
            )
        except ImportError:
            # Se o modelo SlowRequest não estiver disponível, ignora
            pass
        except Exception as e:
            # Ignora erros para não afetar a resposta
            if settings.DEBUG:
                print(f"Erro ao registrar requisição lenta: {e}")


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware para rastrear a atividade do usuário.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Atualiza a última atividade do usuário
            try:
                from django.utils import timezone
                request.user.profile.last_activity = timezone.now()
                request.user.profile.save(update_fields=['last_activity'])
            except Exception:
                # Ignora erros para não afetar a requisição
                pass
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para adicionar cabeçalhos de segurança às respostas.
    """
    
    def process_response(self, request, response):
        # Content Security Policy (CSP)
        if not response.has_header('Content-Security-Policy'):
            csp = getattr(settings, 'CONTENT_SECURITY_POLICY', None)
            if csp:
                response['Content-Security-Policy'] = csp
        
        # X-Content-Type-Options
        if not response.has_header('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        if not response.has_header('X-Frame-Options'):
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # X-XSS-Protection
        if not response.has_header('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        if not response.has_header('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Strict-Transport-Security (HSTS)
        if not response.has_header('Strict-Transport-Security') and request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class JsonRequestMiddleware(MiddlewareMixin):
    """
    Middleware para processar requisições JSON.
    """
    
    def process_request(self, request):
        if request.content_type == 'application/json':
            try:
                request.json = json.loads(request.body)
            except json.JSONDecodeError:
                request.json = None
        
        return None


class MobileDetectionMiddleware(MiddlewareMixin):
    """
    Middleware para detectar dispositivos móveis.
    """
    
    def process_request(self, request):
        # Padrão para detectar dispositivos móveis
        mobile_pattern = re.compile(r'Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini', re.IGNORECASE)
        
        # Verifica se o User-Agent indica um dispositivo móvel
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        request.is_mobile = bool(mobile_pattern.search(user_agent))
        
        return None


class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware para definir o fuso horário do usuário.
    """
    
    def process_request(self, request):
        from django.utils import timezone
        import pytz
        
        # Define o fuso horário padrão
        default_timezone = getattr(settings, 'DEFAULT_TIMEZONE', 'America/Sao_Paulo')
        
        # Se o usuário estiver autenticado e tiver um fuso horário definido
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_timezone = request.user.profile.timezone or default_timezone
        else:
            # Tenta obter o fuso horário da sessão
            user_timezone = request.session.get('timezone', default_timezone)
        
        # Define o fuso horário atual
        try:
            timezone.activate(pytz.timezone(user_timezone))
        except pytz.exceptions.UnknownTimeZoneError:
            # Se o fuso horário for inválido, usa o padrão
            timezone.activate(pytz.timezone(default_timezone))
        
        return None


class LanguageMiddleware(MiddlewareMixin):
    """
    Middleware para definir o idioma do usuário.
    """
    
    def process_request(self, request):
        from django.utils import translation
        
        # Define o idioma padrão
        default_language = getattr(settings, 'LANGUAGE_CODE', 'pt-br')
        
        # Se o usuário estiver autenticado e tiver um idioma definido
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_language = request.user.profile.language or default_language
        else:
            # Tenta obter o idioma da sessão
            user_language = request.session.get('language', default_language)
        
        # Define o idioma atual
        translation.activate(user_language)
        
        return None


class AuthenticationRedirectMiddleware(MiddlewareMixin):
    """
    Middleware para garantir redirecionamento correto para login quando usuário não está autenticado.
    """
    
    def process_request(self, request):
        # Lista de URLs que requerem autenticação
        protected_urls = [
            '/vacancies/vagas-disponiveis/',
            '/vacancies/recruiter/',
            '/administration/',
            '/users/profile/',
        ]
        
        # Verifica se a URL atual requer autenticação
        requires_auth = any(request.path.startswith(url) for url in protected_urls)
        
        if requires_auth and not request.user.is_authenticated:
            # Se for uma requisição AJAX, retorna erro JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': settings.LOGIN_URL
                }, status=401)
            
            # Redireciona para a página de login com o parâmetro next
            from django.urls import reverse
            login_url = reverse('users:login')
            next_url = request.get_full_path()
            return HttpResponseRedirect(f"{login_url}?next={next_url}")
        
        return None
