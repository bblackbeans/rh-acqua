"""
URLs para o sistema de email
"""
from django.urls import path
from . import views

app_name = 'email_system'

urlpatterns = [
    # Dashboard
    path('', views.email_dashboard, name='dashboard'),
    
    # Fila de emails
    path('queue/', views.email_queue_view, name='queue'),
    path('queue/<int:email_id>/retry/', views.retry_email, name='retry_email'),
    path('queue/<int:email_id>/cancel/', views.cancel_email, name='cancel_email'),
    
    # Logs
    path('logs/', views.email_logs_view, name='logs'),
    
    # API
    path('api/test-email/', views.TestEmailView.as_view(), name='test_email'),
    path('api/stats/', views.email_stats_api, name='stats_api'),
]
