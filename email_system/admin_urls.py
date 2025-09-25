"""
URLs administrativas para o sistema de email integradas ao Django Admin
"""
from django.urls import path
from . import admin_views

app_name = 'admin_email_system'

urlpatterns = [
    # Dashboard
    path('', admin_views.email_dashboard_admin, name='dashboard'),
    
    # Fila de emails
    path('queue/', admin_views.email_queue_admin, name='queue'),
    path('queue/<int:email_id>/retry/', admin_views.retry_email_admin, name='retry_email'),
    path('queue/<int:email_id>/cancel/', admin_views.cancel_email_admin, name='cancel_email'),
    
    # Logs
    path('logs/', admin_views.email_logs_admin, name='logs'),
    
    # API
    path('api/test-email/', admin_views.TestEmailAdminView.as_view(), name='test_email'),
    path('api/stats/', admin_views.email_stats_api_admin, name='stats_api'),
]
