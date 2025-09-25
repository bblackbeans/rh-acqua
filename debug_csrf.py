#!/usr/bin/env python3
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from django.conf import settings

print("=== CONFIGURAÇÕES DE CSRF ===")
print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
print(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not set')}")
print(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Not set')}")
print(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Not set')}")
print(f"CSRF_USE_SESSIONS: {getattr(settings, 'CSRF_USE_SESSIONS', 'Not set')}")
print(f"CSRF_FAILURE_VIEW: {getattr(settings, 'CSRF_FAILURE_VIEW', 'Not set')}")
print(f"ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', 'Not set')}")
print(f"DEBUG: {getattr(settings, 'DEBUG', 'Not set')}")

print("\n=== MIDDLEWARE ===")
for i, middleware in enumerate(settings.MIDDLEWARE):
    print(f"{i+1}. {middleware}")

print("\n=== TEMPLATES CONTEXT PROCESSORS ===")
for i, processor in enumerate(settings.TEMPLATES[0]['OPTIONS']['context_processors']):
    print(f"{i+1}. {processor}")
