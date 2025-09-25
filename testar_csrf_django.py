#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')

try:
    django.setup()
    from django.conf import settings
    
    print("🔍 VERIFICANDO CONFIGURAÇÕES DE CSRF NO DJANGO")
    print("=" * 50)
    
    print(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Not set')}")
    print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
    print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'Not set')}")
    print(f"ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', 'Not set')}")
    print(f"DEBUG: {getattr(settings, 'DEBUG', 'Not set')}")
    
    print("\n🔍 TESTANDO ORIGEM HTTPS:")
    print("=" * 30)
    
    # Testar se o domínio HTTPS está nas origens confiáveis
    trusted_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
    https_domain = "https://rh.institutoacqua.org.br"
    
    if https_domain in trusted_origins:
        print(f"✅ {https_domain} está nas origens confiáveis")
    else:
        print(f"❌ {https_domain} NÃO está nas origens confiáveis")
        print(f"Origens atuais: {trusted_origins}")
    
    print("\n🔍 CONFIGURAÇÕES DE SEGURANÇA:")
    print("=" * 35)
    
    secure_ssl_redirect = getattr(settings, 'SECURE_SSL_REDIRECT', False)
    secure_browser_xss_filter = getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)
    secure_content_type_nosniff = getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False)
    
    print(f"SECURE_SSL_REDIRECT: {secure_ssl_redirect}")
    print(f"SECURE_BROWSER_XSS_FILTER: {secure_browser_xss_filter}")
    print(f"SECURE_CONTENT_TYPE_NOSNIFF: {secure_content_type_nosniff}")
    
    print("\n✅ Verificação concluída!")
    
except Exception as e:
    print(f"❌ Erro ao verificar configurações: {e}")
    sys.exit(1)
